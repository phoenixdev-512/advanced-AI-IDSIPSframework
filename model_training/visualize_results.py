#!/usr/bin/env python3
"""
Visualize model training results
"""

import argparse
import logging
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)


def plot_model_comparison(df: pd.DataFrame, output_dir: Path):
    """Plot model comparison bar charts
    
    Args:
        df: DataFrame with model comparison results
        output_dir: Output directory for plots
    """
    logger.info("Creating model comparison plots...")
    
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    
    # Create subplots
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Model Performance Comparison', fontsize=16, fontweight='bold')
    
    for idx, metric in enumerate(metrics):
        ax = axes[idx // 3, idx % 3]
        
        # Sort by metric
        df_sorted = df.sort_values(metric, ascending=False)
        
        # Create bar plot
        bars = ax.bar(df_sorted['Model'], df_sorted[metric], color='steelblue', alpha=0.8)
        
        # Highlight best model
        bars[0].set_color('green')
        bars[0].set_alpha(1.0)
        
        # Formatting
        ax.set_ylabel(metric, fontsize=12)
        ax.set_xlabel('Model', fontsize=12)
        ax.set_title(f'{metric} by Model', fontsize=13, fontweight='bold')
        ax.set_ylim([0, 1.1])
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.3f}',
                   ha='center', va='bottom', fontsize=10)
        
        # Rotate x labels
        ax.tick_params(axis='x', rotation=45)
    
    # Remove empty subplot
    fig.delaxes(axes[1, 2])
    
    plt.tight_layout()
    output_path = output_dir / 'model_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved comparison plot to {output_path}")


def plot_metrics_heatmap(df: pd.DataFrame, output_dir: Path):
    """Plot heatmap of all metrics
    
    Args:
        df: DataFrame with model comparison results
        output_dir: Output directory for plots
    """
    logger.info("Creating metrics heatmap...")
    
    # Prepare data
    metrics_cols = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    heatmap_data = df.set_index('Model')[metrics_cols]
    
    # Create heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(heatmap_data.T, annot=True, fmt='.3f', cmap='YlGnBu',
                cbar_kws={'label': 'Score'}, vmin=0, vmax=1)
    
    plt.title('Model Performance Heatmap', fontsize=14, fontweight='bold')
    plt.xlabel('Model', fontsize=12)
    plt.ylabel('Metric', fontsize=12)
    plt.tight_layout()
    
    output_path = output_dir / 'metrics_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved heatmap to {output_path}")


def plot_precision_recall_tradeoff(df: pd.DataFrame, output_dir: Path):
    """Plot precision-recall trade-off
    
    Args:
        df: DataFrame with model comparison results
        output_dir: Output directory for plots
    """
    logger.info("Creating precision-recall plot...")
    
    plt.figure(figsize=(10, 8))
    
    for idx, row in df.iterrows():
        plt.scatter(row['Recall'], row['Precision'], s=200, alpha=0.7,
                   label=row['Model'])
        plt.annotate(row['Model'], 
                    (row['Recall'], row['Precision']),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=10)
    
    plt.xlabel('Recall (Sensitivity)', fontsize=12)
    plt.ylabel('Precision', fontsize=12)
    plt.title('Precision-Recall Trade-off', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.xlim([0, 1.05])
    plt.ylim([0, 1.05])
    
    # Add diagonal line (F1 contours would be ideal, but this is simpler)
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.3, label='Equal Precision-Recall')
    
    plt.legend(loc='lower left')
    plt.tight_layout()
    
    output_path = output_dir / 'precision_recall_tradeoff.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved precision-recall plot to {output_path}")


def plot_roc_comparison(df: pd.DataFrame, output_dir: Path):
    """Plot ROC-AUC comparison
    
    Args:
        df: DataFrame with model comparison results
        output_dir: Output directory for plots
    """
    logger.info("Creating ROC-AUC comparison...")
    
    plt.figure(figsize=(10, 6))
    
    # Sort by ROC-AUC
    df_sorted = df.sort_values('ROC-AUC', ascending=True)
    
    # Create horizontal bar plot
    bars = plt.barh(df_sorted['Model'], df_sorted['ROC-AUC'], color='coral', alpha=0.8)
    
    # Highlight best
    bars[-1].set_color('darkgreen')
    bars[-1].set_alpha(1.0)
    
    plt.xlabel('ROC-AUC Score', fontsize=12)
    plt.ylabel('Model', fontsize=12)
    plt.title('ROC-AUC Comparison', fontsize=14, fontweight='bold')
    plt.xlim([0, 1.1])
    plt.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f'{width:.3f}',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    output_path = output_dir / 'roc_auc_comparison.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved ROC-AUC plot to {output_path}")


def create_summary_dashboard(df: pd.DataFrame, output_dir: Path):
    """Create a summary dashboard with key metrics
    
    Args:
        df: DataFrame with model comparison results
        output_dir: Output directory for plots
    """
    logger.info("Creating summary dashboard...")
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # 1. Overall scores
    ax1 = fig.add_subplot(gs[0, :])
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC']
    x = np.arange(len(df))
    width = 0.15
    
    for i, metric in enumerate(metrics):
        offset = width * (i - 2)
        ax1.bar(x + offset, df[metric], width, label=metric, alpha=0.8)
    
    ax1.set_xlabel('Model', fontsize=12)
    ax1.set_ylabel('Score', fontsize=12)
    ax1.set_title('All Metrics Comparison', fontsize=13, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['Model'], rotation=0)
    ax1.legend(loc='lower right')
    ax1.grid(axis='y', alpha=0.3)
    ax1.set_ylim([0, 1.1])
    
    # 2. Precision-Recall scatter
    ax2 = fig.add_subplot(gs[1, 0])
    for idx, row in df.iterrows():
        ax2.scatter(row['Recall'], row['Precision'], s=150, alpha=0.7)
        ax2.annotate(row['Model'], (row['Recall'], row['Precision']),
                    fontsize=9, ha='center')
    ax2.set_xlabel('Recall', fontsize=11)
    ax2.set_ylabel('Precision', fontsize=11)
    ax2.set_title('Precision vs Recall', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim([0, 1.05])
    ax2.set_ylim([0, 1.05])
    
    # 3. F1-Score ranking
    ax3 = fig.add_subplot(gs[1, 1])
    df_sorted = df.sort_values('F1-Score', ascending=True)
    colors = ['green' if i == len(df_sorted)-1 else 'steelblue' 
              for i in range(len(df_sorted))]
    ax3.barh(df_sorted['Model'], df_sorted['F1-Score'], color=colors, alpha=0.8)
    ax3.set_xlabel('F1-Score', fontsize=11)
    ax3.set_title('F1-Score Ranking', fontsize=12, fontweight='bold')
    ax3.grid(axis='x', alpha=0.3)
    
    # 4. Best model summary
    ax4 = fig.add_subplot(gs[2, :])
    ax4.axis('off')
    
    best_model = df.iloc[df['F1-Score'].idxmax()]
    summary_text = f"""
    BEST MODEL: {best_model['Model']}
    
    Performance Metrics:
    • Accuracy:   {best_model['Accuracy']:.4f}
    • Precision:  {best_model['Precision']:.4f} (Low false alarms)
    • Recall:     {best_model['Recall']:.4f} (High threat detection)
    • F1-Score:   {best_model['F1-Score']:.4f}
    • ROC-AUC:    {best_model['ROC-AUC']:.4f}
    
    Recommendation: Deploy {best_model['Model']} for production use
    """
    
    ax4.text(0.5, 0.5, summary_text, 
            ha='center', va='center',
            fontsize=12,
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3),
            family='monospace')
    
    fig.suptitle('Model Training Summary Dashboard', 
                fontsize=16, fontweight='bold', y=0.98)
    
    output_path = output_dir / 'summary_dashboard.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Saved summary dashboard to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Visualize model training results")
    parser.add_argument('--results', type=str, required=True,
                       help='Path to comparison results CSV')
    parser.add_argument('--output', type=str, default='model_training/results/plots/',
                       help='Output directory for plots')
    
    args = parser.parse_args()
    
    # Load results
    logger.info(f"Loading results from {args.results}...")
    
    results_path = Path(args.results)
    if results_path.is_dir():
        # Look for comparison.csv in directory
        csv_path = results_path / 'comparison.csv'
    else:
        csv_path = results_path
    
    if not csv_path.exists():
        logger.error(f"Results file not found: {csv_path}")
        return
    
    df = pd.read_csv(csv_path)
    logger.info(f"Loaded results for {len(df)} models")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate plots
    plot_model_comparison(df, output_dir)
    plot_metrics_heatmap(df, output_dir)
    plot_precision_recall_tradeoff(df, output_dir)
    plot_roc_comparison(df, output_dir)
    create_summary_dashboard(df, output_dir)
    
    logger.info(f"\nAll plots saved to {output_dir}")
    logger.info("Visualization completed successfully!")


if __name__ == "__main__":
    main()
