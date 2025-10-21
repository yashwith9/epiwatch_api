#!/usr/bin/env python3
"""
EpiWatch Data Ingestion CLI

Command-line interface for running data ingestion services.
Supports one-time collection, continuous monitoring, and status checks.

Usage:
    python -m ingest.cli collect-once
    python -m ingest.cli start-continuous
    python -m ingest.cli status
    python -m ingest.cli test-sources

Author: EpiWatch Team
License: MIT
"""

import asyncio
import logging
import sys
import click
from datetime import datetime
from typing import Dict, Any

from .collectors import DataIngestionOrchestrator, RSSCollector, NewsAPICollector
from .storage import DatabaseStorage, RedisQueue
from .config import config


# Setup logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(config.log_file, mode='a') if config.log_file else logging.NullHandler()
    ]
)

logger = logging.getLogger(__name__)


@click.group()
def cli():
    """EpiWatch Data Ingestion CLI"""
    pass


@cli.command()
def validate_config():
    """Validate configuration settings"""
    click.echo("🔍 Validating EpiWatch Ingestion Configuration...")
    
    errors = config.validate_config()
    
    if errors:
        click.echo("❌ Configuration errors found:")
        for error in errors:
            click.echo(f"  - {error}")
        sys.exit(1)
    else:
        click.echo("✅ Configuration is valid!")
    
    # Show configuration summary
    click.echo("\n📋 Configuration Summary:")
    click.echo(f"  RSS Sources: {len(config.get_enabled_rss_sources())}")
    click.echo(f"  API Sources: {len(config.get_enabled_apis())}")
    click.echo(f"  Collection Interval: {config.collection_interval} minutes")
    click.echo(f"  Batch Size: {config.batch_size}")
    click.echo(f"  Log Level: {config.log_level}")


@cli.command()
def init_database():
    """Initialize database tables"""
    async def _init_db():
        click.echo("🗃️ Initializing database...")
        
        db_storage = DatabaseStorage()
        try:
            await db_storage.initialize_database()
            click.echo("✅ Database tables created successfully!")
        except Exception as e:
            click.echo(f"❌ Database initialization failed: {e}")
            sys.exit(1)
        finally:
            await db_storage.close()
    
    asyncio.run(_init_db())


@cli.command()
def test_sources():
    """Test connectivity to all configured sources"""
    async def _test_sources():
        click.echo("🔌 Testing source connectivity...")
        
        # Test RSS sources
        rss_collector = RSSCollector()
        rss_sources = config.get_enabled_rss_sources()
        
        click.echo(f"\n📡 Testing {len(rss_sources)} RSS sources:")
        
        for source in rss_sources[:3]:  # Test first 3 to avoid rate limits
            try:
                articles = await rss_collector.collect_from_source(source)
                status = "✅" if articles else "⚠️ (no articles)"
                click.echo(f"  {source.name}: {status}")
            except Exception as e:
                click.echo(f"  {source.name}: ❌ ({str(e)[:50]}...)")
        
        # Test APIs
        api_configs = config.get_enabled_apis()
        click.echo(f"\n🔗 Testing {len(api_configs)} API sources:")
        
        if "newsapi" in api_configs:
            try:
                newsapi_collector = NewsAPICollector()
                articles = await newsapi_collector.collect_health_news()
                status = "✅" if articles else "⚠️ (no articles)"
                click.echo(f"  NewsAPI: {status}")
            except Exception as e:
                click.echo(f"  NewsAPI: ❌ ({str(e)[:50]}...)")
        
        # Test Redis connection
        click.echo("\n🗄️ Testing Redis connection:")
        try:
            redis_queue = RedisQueue()
            stats = await redis_queue.get_queue_stats()
            click.echo(f"  Redis: ✅ (queues: {sum(stats.values())} items)")
            await redis_queue.close()
        except Exception as e:
            click.echo(f"  Redis: ❌ ({str(e)[:50]}...)")
        
        # Test Database connection
        click.echo("\n🗃️ Testing database connection:")
        try:
            db_storage = DatabaseStorage()
            await db_storage._get_engine()  # Test connection
            click.echo("  Database: ✅")
            await db_storage.close()
        except Exception as e:
            click.echo(f"  Database: ❌ ({str(e)[:50]}...)")
    
    asyncio.run(_test_sources())


@cli.command()
def collect_once():
    """Run one collection cycle"""
    async def _collect_once():
        click.echo("🚀 Starting single collection cycle...")
        
        orchestrator = DataIngestionOrchestrator()
        
        try:
            start_time = datetime.now()
            stats = await orchestrator.run_collection_cycle()
            duration = (datetime.now() - start_time).total_seconds()
            
            click.echo("✅ Collection completed!")
            click.echo(f"📊 Statistics:")
            click.echo(f"  Articles collected: {stats.get('total_articles', 0)}")
            click.echo(f"  Sources processed: {stats.get('sources', 0)}")
            click.echo(f"  Errors encountered: {stats.get('errors', 0)}")
            click.echo(f"  Duration: {duration:.2f} seconds")
            
        except Exception as e:
            click.echo(f"❌ Collection failed: {e}")
            sys.exit(1)
    
    asyncio.run(_collect_once())


@cli.command()
@click.option('--interval', '-i', default=None, type=int, 
              help='Collection interval in minutes (overrides config)')
def start_continuous(interval):
    """Start continuous data collection"""
    if interval:
        config.collection_interval = interval
    
    click.echo("🔄 Starting continuous data collection...")
    click.echo(f"⏱️ Collection interval: {config.collection_interval} minutes")
    click.echo("Press Ctrl+C to stop")
    
    async def _continuous_collection():
        orchestrator = DataIngestionOrchestrator()
        
        try:
            await orchestrator.run_continuous_collection()
        except KeyboardInterrupt:
            click.echo("\n⏹️ Collection stopped by user")
        except Exception as e:
            click.echo(f"\n❌ Collection failed: {e}")
            sys.exit(1)
    
    asyncio.run(_continuous_collection())


@cli.command()
def status():
    """Show system status and statistics"""
    async def _show_status():
        click.echo("📊 EpiWatch Ingestion Status")
        click.echo("=" * 40)
        
        # Queue statistics
        try:
            redis_queue = RedisQueue()
            queue_stats = await redis_queue.get_queue_stats()
            
            click.echo("🗄️ Queue Status:")
            click.echo(f"  NLP Queue: {queue_stats.get('nlp_queue_size', 0)} items")
            click.echo(f"  Processing Queue: {queue_stats.get('processing_queue_size', 0)} items")
            click.echo(f"  Alerts Queue: {queue_stats.get('alerts_queue_size', 0)} items")
            
            await redis_queue.close()
        except Exception as e:
            click.echo(f"❌ Queue status unavailable: {e}")
        
        # Database statistics
        try:
            db_storage = DatabaseStorage()
            
            # Get pending articles count
            pending_articles = await db_storage.get_pending_articles(limit=1000)
            click.echo(f"\n🗃️ Database Status:")
            click.echo(f"  Pending articles: {len(pending_articles)}")
            
            await db_storage.close()
        except Exception as e:
            click.echo(f"❌ Database status unavailable: {e}")
        
        # Configuration status
        click.echo(f"\n⚙️ Configuration:")
        click.echo(f"  RSS Sources: {len(config.get_enabled_rss_sources())}")
        click.echo(f"  API Sources: {len(config.get_enabled_apis())}")
        click.echo(f"  Collection Interval: {config.collection_interval} minutes")
        
        # Recent errors check
        errors = config.validate_config()
        if errors:
            click.echo(f"\n⚠️ Configuration Issues:")
            for error in errors:
                click.echo(f"  - {error}")
    
    asyncio.run(_show_status())


@cli.command()
def clear_queues():
    """Clear all Redis queues (use with caution)"""
    if not click.confirm("⚠️ This will clear all queues. Are you sure?"):
        return
    
    async def _clear_queues():
        try:
            redis_queue = RedisQueue()
            await redis_queue.clear_queues()
            click.echo("✅ All queues cleared")
            await redis_queue.close()
        except Exception as e:
            click.echo(f"❌ Failed to clear queues: {e}")
    
    asyncio.run(_clear_queues())


@cli.command()
@click.option('--source', '-s', help='Test specific RSS source by name')
def test_rss(source):
    """Test RSS feed collection"""
    async def _test_rss():
        rss_collector = RSSCollector()
        sources = config.get_enabled_rss_sources()
        
        if source:
            # Find specific source
            target_sources = [s for s in sources if source.lower() in s.name.lower()]
            if not target_sources:
                click.echo(f"❌ Source '{source}' not found")
                return
            sources = target_sources
        
        for rss_source in sources:
            click.echo(f"🔍 Testing: {rss_source.name}")
            try:
                articles = await rss_collector.collect_from_source(rss_source)
                click.echo(f"  ✅ Collected {len(articles)} articles")
                
                if articles:
                    sample = articles[0]
                    click.echo(f"  📝 Sample title: {sample.title[:100]}...")
                    click.echo(f"  🔗 URL: {sample.url}")
                    click.echo(f"  📅 Published: {sample.published_at}")
                
            except Exception as e:
                click.echo(f"  ❌ Error: {e}")
            
            click.echo()
    
    asyncio.run(_test_rss())


if __name__ == "__main__":
    cli()