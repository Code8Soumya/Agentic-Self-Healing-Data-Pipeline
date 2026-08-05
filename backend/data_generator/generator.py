"""Main event generator orchestrator.

CONNECTIONS:
- Imports: All event generators (order_events, inventory_events, user_activity_events)
           drift_injector, anomaly_injector, scenarios
           app.config.get_settings (for Pub/Sub topic names)
- Called by: Makefile 'make generate-events'
              scripts (CLI entry point)
              api/triggers.py (for manual injection)
- Publishes to: Pub/Sub 'raw-ecommerce-events' topic (via google.cloud.pubsub)

FLOW:
  1. Generate batch of normal events (mix of order, inventory, user_activity)
  2. Optionally inject drift/anomalies at configurable rate (e.g., 5% of events)
  3. Serialize each event to JSON
  4. Publish to Pub/Sub topic
  5. Log statistics (events generated, drift injected, etc.)

USAGE:
  python -m data_generator.generator --events-per-second 10 --duration 60 --drift-rate 0.05
"""
import argparse
import json
import logging
import time
from typing import Optional

import random
from google.cloud import pubsub_v1

from data_generator.order_events import generate_order_event
from data_generator.inventory_events import generate_inventory_event
from data_generator.user_activity_events import generate_user_activity_event
from data_generator.drift_injector import inject_random_drift
from data_generator.anomaly_injector import inject_random_anomaly
from data_generator.scenarios import ScenarioConfig, SCENARIOS

logger = logging.getLogger(__name__)


class EventGeneratorOrchestrator:
    """Orchestrates event generation and publishes to Pub/Sub.
    
    This is the main entry point for generating test data.
    It creates a mix of event types, optionally injects failures,
    and publishes everything to the raw-ecommerce-events Pub/Sub topic.
    
    Args:
        project_id: GCP project ID
        topic_name: Pub/Sub topic to publish to (default: raw-ecommerce-events)
        drift_rate: Fraction of events to inject with schema drift (0.0-1.0, default 0.0)
        anomaly_rate: Fraction of events to inject with DQ anomalies (0.0-1.0, default 0.0)
        event_mix: Dict of event type weights, e.g., {"order": 0.5, "inventory": 0.3, "user_activity": 0.2}
    
    CONNECTIONS:
        - Uses: google.cloud.pubsub_v1.PublisherClient for Pub/Sub publishing
        - Config: Reads topic names from app.config.get_settings()
    """
    
    def __init__(
        self,
        project_id: str,
        topic_name: str = "raw-ecommerce-events",
        drift_rate: float = 0.0,
        anomaly_rate: float = 0.0,
        event_mix: Optional[dict[str, float]] = None,
    ) -> None:
        self.project_id = project_id
        self.topic_name = topic_name
        self.drift_rate = drift_rate
        self.anomaly_rate = anomaly_rate
        self.event_mix = event_mix or {"order": 0.5, "inventory": 0.3, "user_activity": 0.2}
        self.publisher = pubsub_v1.PublisherClient()
        self.topic_path = self.publisher.topic_path(self.project_id, self.topic_name)
    
    def generate_single_event(self) -> dict:
        """Generate a single event based on the configured event mix.
        
        Returns:
            dict: Serialized event. May have drift/anomaly injected
                  based on drift_rate and anomaly_rate.
        
        LOGIC:
            1. Pick event type based on event_mix weights (random.choices)
            2. Call the appropriate generator (order/inventory/user_activity)
            3. Serialize to dict with .model_dump()
            4. With probability drift_rate, inject a random drift
            5. With probability anomaly_rate, inject a random anomaly
            6. Return the dict
        """
        event_types = list(self.event_mix.keys())
        weights = list(self.event_mix.values())
        chosen_type = random.choices(event_types, weights=weights, k=1)[0]
        
        if chosen_type == "order":
            event = generate_order_event()
        elif chosen_type == "inventory":
            event = generate_inventory_event()
        else:
            event = generate_user_activity_event()
            
        event_dict = event.model_dump()
        
        if random.random() < self.drift_rate:
            event_dict, _ = inject_random_drift(event_dict)
            
        if random.random() < self.anomaly_rate:
            event_dict, _ = inject_random_anomaly(event_dict)
            
        return event_dict
    
    def publish_event(self, event_dict: dict) -> str:
        """Publish a single event to Pub/Sub.
        
        Args:
            event_dict: Serialized event as dict
        
        Returns:
            str: Published message ID from Pub/Sub
        
        LOGIC:
            1. json.dumps(event_dict, default=str) to handle datetime serialization
            2. publisher.publish(topic_path, data=json_bytes)
            3. Return future.result() (the message ID)
        """
        json_bytes = json.dumps(event_dict, default=str).encode("utf-8")
        future = self.publisher.publish(self.topic_path, data=json_bytes)
        return future.result()
    
    def run(
        self,
        events_per_second: int = 10,
        duration_seconds: int = 60,
    ) -> dict:
        """Run the generator for a specified duration.
        
        Args:
            events_per_second: Target event generation rate
            duration_seconds: How long to run (0 = infinite)
        
        Returns:
            dict: Statistics summary:
                {
                    "total_events": int,
                    "events_by_type": {"order": N, "inventory": N, ...},
                    "drift_injected": int,
                    "anomalies_injected": int,
                    "duration_seconds": float,
                    "avg_events_per_second": float,
                }
        
        LOGIC:
            1. Loop for duration_seconds
            2. Each second, generate events_per_second events
            3. Publish each event
            4. Sleep to maintain rate
            5. Log progress every 10 seconds
            6. Return stats dict
        """
        stats = {
            "total_events": 0,
            "events_by_type": {"order": 0, "inventory": 0, "user_activity": 0},
            "drift_injected": 0,
            "anomalies_injected": 0,
            "duration_seconds": duration_seconds,
            "avg_events_per_second": 0.0,
        }
        
        start_time = time.time()
        end_time = start_time + duration_seconds if duration_seconds > 0 else float('inf')
        
        try:
            while time.time() < end_time:
                loop_start = time.time()
                for _ in range(events_per_second):
                    event_dict = self.generate_single_event()
                    event_type = event_dict.get("event_type", "unknown")
                    
                    if event_type in stats["events_by_type"]:
                        stats["events_by_type"][event_type] += 1
                    else:
                        stats["events_by_type"][event_type] = 1
                    
                    self.publish_event(event_dict)
                    stats["total_events"] += 1
                
                elapsed = time.time() - loop_start
                sleep_time = max(0.0, 1.0 - elapsed)
                time.sleep(sleep_time)
                
                if int(time.time() - start_time) % 10 == 0:
                    logger.info(f"Generated {stats['total_events']} events so far...")
                    
        except KeyboardInterrupt:
            logger.info("Interrupted by user.")
            
        actual_duration = time.time() - start_time
        stats["duration_seconds"] = actual_duration
        if actual_duration > 0:
            stats["avg_events_per_second"] = stats["total_events"] / actual_duration
            
        return stats
    
    def run_scenario(self, scenario: ScenarioConfig, count: int = 1) -> list[dict]:
        """Run a specific failure scenario.
        
        Args:
            scenario: ScenarioConfig defining the failure to inject
            count: Number of events to generate with this failure
        
        Returns:
            list[dict]: The generated (mutated) events
        
        LOGIC:
            1. Generate 'count' events of scenario.event_type
            2. If scenario.failure_mode == "drift": inject_drift with scenario.drift_type
            3. If scenario.failure_mode == "anomaly": inject_anomaly with scenario.anomaly_type
            4. Publish all events
            5. Return the mutated event dicts
        """
        mutated_events = []
        for _ in range(count):
            if scenario.event_type == "order":
                event = generate_order_event().model_dump()
            elif scenario.event_type == "inventory":
                event = generate_inventory_event().model_dump()
            else:
                event = generate_user_activity_event().model_dump()
                
            if scenario.failure_mode == "drift" and scenario.drift_type:
                from data_generator.drift_injector import inject_drift
                event = inject_drift(event, scenario.drift_type)
            elif scenario.failure_mode == "anomaly" and scenario.anomaly_type:
                from data_generator.anomaly_injector import inject_anomaly
                event = inject_anomaly(event, scenario.anomaly_type)
                
            self.publish_event(event)
            mutated_events.append(event)
            
        return mutated_events


def main():
    """CLI entry point for the event generator.
    
    Usage:
        python -m data_generator.generator --events-per-second 10 --duration 60 --drift-rate 0.05
    
    Args (CLI):
        --project-id: GCP project ID (or from env GCP_PROJECT_ID)
        --topic: Pub/Sub topic name (default: raw-ecommerce-events)
        --events-per-second: Target rate (default: 10)
        --duration: Seconds to run, 0=infinite (default: 60)
        --drift-rate: Fraction of events with drift (default: 0.0)
        --anomaly-rate: Fraction of events with anomalies (default: 0.0)
        --scenario: Run a specific named scenario from scenarios.py
    """
    parser = argparse.ArgumentParser(description="E-commerce Event Generator")
    parser.add_argument("--project-id", type=str, required=True, help="GCP project ID")
    parser.add_argument("--topic", type=str, default="raw-ecommerce-events", help="Pub/Sub topic name")
    parser.add_argument("--events-per-second", type=int, default=10, help="Target rate")
    parser.add_argument("--duration", type=int, default=60, help="Seconds to run (0=infinite)")
    parser.add_argument("--drift-rate", type=float, default=0.0, help="Fraction of events with drift")
    parser.add_argument("--anomaly-rate", type=float, default=0.0, help="Fraction of events with anomalies")
    parser.add_argument("--scenario", type=str, help="Run a specific named scenario")
    
    args = parser.parse_args()
    
    orchestrator = EventGeneratorOrchestrator(
        project_id=args.project_id,
        topic_name=args.topic,
        drift_rate=args.drift_rate,
        anomaly_rate=args.anomaly_rate
    )
    
    if args.scenario:
        if args.scenario in SCENARIOS:
            scenario_config = SCENARIOS[args.scenario]
            orchestrator.run_scenario(scenario_config, count=10)
            logger.info(f"Ran scenario: {args.scenario}")
        else:
            logger.error(f"Scenario not found: {args.scenario}")
    else:
        stats = orchestrator.run(
            events_per_second=args.events_per_second,
            duration_seconds=args.duration
        )
        logger.info(f"Generation complete. Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
