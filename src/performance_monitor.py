#!/usr/bin/env python3
"""
Performance Monitor - Canvas Performance Optimization
Monitors and optimizes canvas rendering performance for multiple annotations.
"""

import time
import logging
from collections import deque
from typing import Dict, Any, Optional
import psutil
import os

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitors and optimizes canvas performance."""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        
        # Performance metrics
        self.update_times = deque(maxlen=history_size)
        self.annotation_counts = deque(maxlen=history_size)
        self.memory_usage = deque(maxlen=history_size)
        
        # Performance thresholds
        self.slow_update_threshold = 0.1  # 100ms
        self.memory_warning_threshold = 512 * 1024 * 1024  # 512MB
        
        # Optimization flags
        self.enable_lazy_updates = True
        self.enable_batch_updates = True
        self.enable_smart_rendering = True
        
        # Update tracking
        self.last_update_time = 0.0
        self.pending_updates = False
        self.update_timer = None
        
        logger.info("Monitor: Performance Monitor initialized")
    
    def start_update_timing(self) -> float:
        """Start timing an update operation."""
        return time.time()
    
    def end_update_timing(self, start_time: float, annotation_count: int) -> float:
        """End timing and record metrics."""
        
        update_duration = time.time() - start_time
        
        # Record metrics
        self.update_times.append(update_duration)
        self.annotation_counts.append(annotation_count)
        
        # Record memory usage
        try:
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / (1024 * 1024)
            self.memory_usage.append(memory_mb)
        except:
            self.memory_usage.append(0)
        
        # Check for performance issues
        if update_duration > self.slow_update_threshold:
            logger.warning(f"Warning: Slow update detected: {update_duration:.3f}s with {annotation_count} annotations")
        
        return update_duration
    
    def should_skip_update(self, current_time: float = None) -> bool:
        """Check if update should be skipped for performance."""
        
        if not self.enable_lazy_updates:
            return False
        
        if current_time is None:
            current_time = time.time()
        
        # Skip if last update was very recent (< 16ms for 60fps)
        time_since_last = current_time - self.last_update_time
        if time_since_last < 0.016:
            self.pending_updates = True
            return True
        
        return False
    
    def mark_update_completed(self):
        """Mark that an update has been completed."""
        self.last_update_time = time.time()
        self.pending_updates = False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        
        if not self.update_times:
            return {
                'avg_update_time': 0.0,
                'max_update_time': 0.0,
                'avg_annotation_count': 0,
                'slow_updates': 0,
                'memory_usage_mb': 0.0
            }
        
        # Calculate statistics
        avg_update_time = sum(self.update_times) / len(self.update_times)
        max_update_time = max(self.update_times)
        avg_annotation_count = sum(self.annotation_counts) / len(self.annotation_counts)
        slow_updates = sum(1 for t in self.update_times if t > self.slow_update_threshold)
        avg_memory = sum(self.memory_usage) / len(self.memory_usage) if self.memory_usage else 0.0
        
        return {
            'avg_update_time': avg_update_time,
            'max_update_time': max_update_time,
            'avg_annotation_count': avg_annotation_count,
            'slow_updates': slow_updates,
            'memory_usage_mb': avg_memory,
            'total_updates': len(self.update_times),
            'performance_score': self._calculate_performance_score()
        }
    
    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)."""
        
        if not self.update_times:
            return 100.0
        
        avg_time = sum(self.update_times) / len(self.update_times)
        
        # Score based on average update time
        if avg_time <= 0.016:  # 60fps
            return 100.0
        elif avg_time <= 0.033:  # 30fps
            return 80.0
        elif avg_time <= 0.05:   # 20fps
            return 60.0
        elif avg_time <= 0.1:    # 10fps
            return 40.0
        else:
            return 20.0
    
    def get_optimization_recommendations(self) -> list:
        """Get performance optimization recommendations."""
        
        recommendations = []
        stats = self.get_performance_stats()
        
        # Check update frequency
        if stats['avg_update_time'] > 0.05:
            recommendations.append("Enable lazy updates to reduce render frequency")
        
        if stats['slow_updates'] > 10:
            recommendations.append("Consider batching annotation operations")
        
        if stats['avg_annotation_count'] > 50:
            recommendations.append("Implement annotation culling for large datasets")
        
        if stats['memory_usage_mb'] > 256:
            recommendations.append("Enable memory optimization for large images")
        
        if len(recommendations) == 0:
            recommendations.append("Performance is optimal")
        
        return recommendations
    
    def log_performance_summary(self):
        """Log a performance summary."""
        
        stats = self.get_performance_stats()
        recommendations = self.get_optimization_recommendations()
        
        logger.info(f"Monitor: Performance Summary:")
        logger.info(f"   Avg Update Time: {stats['avg_update_time']:.3f}s")
        logger.info(f"   Max Update Time: {stats['max_update_time']:.3f}s")
        logger.info(f"   Avg Annotations: {stats['avg_annotation_count']:.1f}")
        logger.info(f"   Slow Updates: {stats['slow_updates']}")
        logger.info(f"   Memory Usage: {stats['memory_usage_mb']:.1f}MB")
        logger.info(f"   Performance Score: {stats['performance_score']:.1f}/100")
        
        for rec in recommendations:
            logger.info(f"   {rec}")


class OptimizedUpdateManager:
    """Manages optimized canvas updates with batching and lazy loading."""
    
    def __init__(self, performance_monitor: PerformanceMonitor):
        self.performance_monitor = performance_monitor
        self.pending_update = False
        self.update_timer = None
        self.batch_delay_ms = 16  # ~60fps
        
    def request_update(self, priority: str = 'normal'):
        """Request a canvas update with optional priority."""
        
        current_time = time.time()
        
        # High priority updates (user actions) bypass optimization
        if priority == 'high':
            return True
        
        # Check if we should skip this update
        if self.performance_monitor.should_skip_update(current_time):
            self.pending_update = True
            return False
        
        return True
    
    def should_update_now(self) -> bool:
        """Check if an update should happen now."""
        return not self.performance_monitor.should_skip_update()
    
    def mark_update_completed(self):
        """Mark that an update has been completed."""
        self.performance_monitor.mark_update_completed()
        self.pending_update = False
