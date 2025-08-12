#!/usr/bin/env python3
"""
Network Analysis Engine for Vanta Ledger
========================================

Analyzes the business network of all 29 companies, providing insights into:
- Company centrality and influence
- Relationship strength and patterns
- Financial flow analysis
- Risk assessment
- Business opportunities

Author: Vanta Ledger Team
"""

import os
import sys
import json
import networkx as nx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
from sqlalchemy import create_engine, text
from pymongo import MongoClient
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NetworkAnalysisEngine:
    """Network analysis engine for business relationship analysis"""
    
    def __init__(self, postgres_engine, mongo_client):
        self.postgres_engine = postgres_engine
        self.mongo_client = mongo_client
        self.mongo_db = mongo_client.vanta_ledger
        self.network_graph = None
        self.analysis_results = {}
        
    def build_network_graph(self):
        """Build NetworkX graph from company relationships"""
        try:
            # Get companies and relationships from PostgreSQL
            with self.postgres_engine.begin() as conn:
                companies = conn.execute(text("""
                    SELECT id, name, company_type, industry 
                    FROM companies 
                    WHERE status = 'active'
                """)).fetchall()
                
                relationships = conn.execute(text("""
                    SELECT cr.company_a_id, cr.company_b_id, cr.relationship_type, 
                           cr.relationship_strength, cr.description,
                           c1.name as company_a_name, c2.name as company_b_name
                    FROM company_relationships cr
                    JOIN companies c1 ON cr.company_a_id = c1.id
                    JOIN companies c2 ON cr.company_b_id = c2.id
                """)).fetchall()
            
            # Create NetworkX graph
            self.network_graph = nx.Graph()
            
            # Add nodes (companies)
            for company in companies:
                self.network_graph.add_node(
                    company[0],  # id
                    name=company[1],  # name
                    company_type=company[2],  # company_type
                    industry=company[3]  # industry
                )
            
            # Add edges (relationships)
            for rel in relationships:
                self.network_graph.add_edge(
                    rel[0],  # company_a_id
                    rel[1],  # company_b_id
                    relationship_type=rel[2],
                    strength=rel[3],
                    description=rel[4]
                )
            
            logger.info(f"✅ Network graph built with {len(companies)} nodes and {len(relationships)} edges")
            
        except Exception as e:
            logger.error(f"❌ Network graph building failed: {e}")
            raise
    
    def calculate_centrality_metrics(self):
        """Calculate various centrality metrics for each company"""
        try:
            if not self.network_graph:
                self.build_network_graph()
            
            centrality_metrics = {}
            
            # Degree centrality
            degree_centrality = nx.degree_centrality(self.network_graph)
            
            # Betweenness centrality
            betweenness_centrality = nx.betweenness_centrality(self.network_graph)
            
            # Closeness centrality
            closeness_centrality = nx.closeness_centrality(self.network_graph)
            
            # Eigenvector centrality
            eigenvector_centrality = nx.eigenvector_centrality(self.network_graph, max_iter=1000)
            
            # PageRank
            pagerank = nx.pagerank(self.network_graph)
            
            # Calculate metrics for each company
            for node in self.network_graph.nodes():
                company_data = self.network_graph.nodes[node]
                centrality_metrics[node] = {
                    'company_id': node,
                    'company_name': company_data['name'],
                    'company_type': company_data['company_type'],
                    'industry': company_data['industry'],
                    'degree_centrality': degree_centrality[node],
                    'betweenness_centrality': betweenness_centrality[node],
                    'closeness_centrality': closeness_centrality[node],
                    'eigenvector_centrality': eigenvector_centrality[node],
                    'pagerank': pagerank[node],
                    'degree': self.network_graph.degree(node),
                    'neighbors_count': len(list(self.network_graph.neighbors(node)))
                }
            
            self.analysis_results['centrality_metrics'] = centrality_metrics
            logger.info("✅ Centrality metrics calculated successfully")
            
        except Exception as e:
            logger.error(f"❌ Centrality metrics calculation failed: {e}")
            raise
    
    def analyze_relationship_patterns(self):
        """Analyze relationship patterns and clusters"""
        try:
            if not self.network_graph:
                self.build_network_graph()
            
            relationship_analysis = {}
            
            # Community detection
            communities = list(nx.community.greedy_modularity_communities(self.network_graph))
            
            # Find cliques
            cliques = list(nx.find_cliques(self.network_graph))
            
            # Analyze relationship types
            relationship_types = {}
            for edge in self.network_graph.edges(data=True):
                rel_type = edge[2]['relationship_type']
                if rel_type not in relationship_types:
                    relationship_types[rel_type] = 0
                relationship_types[rel_type] += 1
            
            # Analyze company type connections
            company_type_connections = {}
            for node in self.network_graph.nodes():
                company_type = self.network_graph.nodes[node]['company_type']
                if company_type not in company_type_connections:
                    company_type_connections[company_type] = {
                        'total_connections': 0,
                        'unique_partners': set()
                    }
                
                neighbors = list(self.network_graph.neighbors(node))
                company_type_connections[company_type]['total_connections'] += len(neighbors)
                company_type_connections[company_type]['unique_partners'].update(neighbors)
            
            # Convert sets to counts
            for company_type in company_type_connections:
                company_type_connections[company_type]['unique_partners_count'] = len(
                    company_type_connections[company_type]['unique_partners']
                )
                del company_type_connections[company_type]['unique_partners']
            
            relationship_analysis = {
                'communities': len(communities),
                'community_details': [list(community) for community in communities],
                'cliques': len(cliques),
                'largest_clique_size': max([len(clique) for clique in cliques]) if cliques else 0,
                'relationship_types': relationship_types,
                'company_type_connections': company_type_connections,
                'network_density': nx.density(self.network_graph),
                'average_clustering': nx.average_clustering(self.network_graph),
                'average_shortest_path': nx.average_shortest_path_length(self.network_graph) if nx.is_connected(self.network_graph) else None
            }
            
            self.analysis_results['relationship_patterns'] = relationship_analysis
            logger.info("✅ Relationship patterns analyzed successfully")
            
        except Exception as e:
            logger.error(f"❌ Relationship pattern analysis failed: {e}")
            raise
    
    def analyze_financial_flows(self):
        """Analyze financial flows between companies"""
        try:
            # Get financial data from ledger entries
            with self.postgres_engine.begin() as conn:
                financial_flows = conn.execute(text("""
                    SELECT 
                        company_id,
                        related_company_id,
                        entry_type,
                        SUM(amount) as total_amount,
                        COUNT(*) as transaction_count,
                        AVG(amount) as avg_amount
                    FROM ledger_entries 
                    WHERE related_company_id IS NOT NULL
                    GROUP BY company_id, related_company_id, entry_type
                """)).fetchall()
            
            financial_analysis = {
                'total_transactions': len(financial_flows),
                'total_volume': sum(flow[3] for flow in financial_flows),
                'flow_details': [],
                'company_flow_summary': {},
                'flow_network': {}
            }
            
            # Analyze flows by company
            company_flows = {}
            for flow in financial_flows:
                company_id = flow[0]
                related_company_id = flow[1]
                entry_type = flow[2]
                amount = flow[3]
                
                if company_id not in company_flows:
                    company_flows[company_id] = {
                        'outgoing': 0,
                        'incoming': 0,
                        'partners': set()
                    }
                
                if entry_type in ['income', 'transfer']:
                    company_flows[company_id]['incoming'] += amount
                else:
                    company_flows[company_id]['outgoing'] += amount
                
                company_flows[company_id]['partners'].add(related_company_id)
                
                # Store flow details
                financial_analysis['flow_details'].append({
                    'from_company': company_id,
                    'to_company': related_company_id,
                    'type': entry_type,
                    'amount': amount,
                    'transaction_count': flow[4],
                    'avg_amount': flow[5]
                })
            
            # Convert sets to counts
            for company_id in company_flows:
                company_flows[company_id]['partner_count'] = len(company_flows[company_id]['partners'])
                del company_flows[company_id]['partners']
            
            financial_analysis['company_flow_summary'] = company_flows
            
            self.analysis_results['financial_flows'] = financial_analysis
            logger.info("✅ Financial flows analyzed successfully")
            
        except Exception as e:
            logger.error(f"❌ Financial flow analysis failed: {e}")
            raise
    
    def assess_risks(self):
        """Assess business risks based on network analysis"""
        try:
            risk_assessment = {
                'high_risk_companies': [],
                'risk_factors': {},
                'recommendations': []
            }
            
            # Analyze centrality-based risks
            if 'centrality_metrics' in self.analysis_results:
                centrality_data = self.analysis_results['centrality_metrics']
                
                # Companies with very high centrality (single point of failure risk)
                high_centrality_threshold = 0.8
                for company_id, metrics in centrality_data.items():
                    if metrics['betweenness_centrality'] > high_centrality_threshold:
                        risk_assessment['high_risk_companies'].append({
                            'company_id': company_id,
                            'company_name': metrics['company_name'],
                            'risk_type': 'high_centrality',
                            'risk_score': metrics['betweenness_centrality'],
                            'description': 'Company has very high centrality - potential single point of failure'
                        })
            
            # Analyze financial concentration risks
            if 'financial_flows' in self.analysis_results:
                financial_data = self.analysis_results['financial_flows']
                company_flows = financial_data['company_flow_summary']
                
                # Companies with high financial concentration
                for company_id, flows in company_flows.items():
                    total_volume = flows['incoming'] + flows['outgoing']
                    if total_volume > 1000000:  # High volume threshold
                        risk_assessment['high_risk_companies'].append({
                            'company_id': company_id,
                            'risk_type': 'high_financial_volume',
                            'risk_score': total_volume / 1000000,  # Normalize
                            'description': f'High financial volume: {total_volume:,.0f} KES'
                        })
            
            # Generate recommendations
            if len(risk_assessment['high_risk_companies']) > 0:
                risk_assessment['recommendations'].append({
                    'type': 'risk_mitigation',
                    'priority': 'high',
                    'description': 'Implement risk mitigation strategies for high-centrality companies',
                    'action_items': [
                        'Diversify business relationships',
                        'Establish backup partnerships',
                        'Implement monitoring systems'
                    ]
                })
            
            self.analysis_results['risk_assessment'] = risk_assessment
            logger.info("✅ Risk assessment completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Risk assessment failed: {e}")
            raise
    
    def generate_insights(self):
        """Generate business insights from network analysis"""
        try:
            insights = {
                'key_findings': [],
                'opportunities': [],
                'trends': [],
                'recommendations': []
            }
            
            # Key findings based on centrality
            if 'centrality_metrics' in self.analysis_results:
                centrality_data = self.analysis_results['centrality_metrics']
                
                # Most influential companies
                top_companies = sorted(
                    centrality_data.items(),
                    key=lambda x: x[1]['pagerank'],
                    reverse=True
                )[:5]
                
                insights['key_findings'].append({
                    'type': 'top_influencers',
                    'title': 'Most Influential Companies',
                    'description': 'Companies with highest network influence',
                    'data': [
                        {
                            'company_name': company[1]['company_name'],
                            'influence_score': company[1]['pagerank'],
                            'company_type': company[1]['company_type']
                        }
                        for company in top_companies
                    ]
                })
            
            # Business opportunities
            if 'relationship_patterns' in self.analysis_results:
                patterns = self.analysis_results['relationship_patterns']
                
                # Identify isolated companies (opportunities for new partnerships)
                isolated_companies = []
                for node in self.network_graph.nodes():
                    if self.network_graph.degree(node) == 0:
                        isolated_companies.append({
                            'company_id': node,
                            'company_name': self.network_graph.nodes[node]['name'],
                            'company_type': self.network_graph.nodes[node]['company_type']
                        })
                
                if isolated_companies:
                    insights['opportunities'].append({
                        'type': 'partnership_opportunity',
                        'title': 'Partnership Opportunities',
                        'description': 'Companies with no current partnerships',
                        'data': isolated_companies
                    })
            
            # Financial insights
            if 'financial_flows' in self.analysis_results:
                financial_data = self.analysis_results['financial_flows']
                
                insights['key_findings'].append({
                    'type': 'financial_summary',
                    'title': 'Financial Network Summary',
                    'description': 'Overview of financial flows in the network',
                    'data': {
                        'total_transactions': financial_data['total_transactions'],
                        'total_volume': financial_data['total_volume'],
                        'average_transaction': financial_data['total_volume'] / financial_data['total_transactions'] if financial_data['total_transactions'] > 0 else 0
                    }
                })
            
            self.analysis_results['insights'] = insights
            logger.info("✅ Business insights generated successfully")
            
        except Exception as e:
            logger.error(f"❌ Insights generation failed: {e}")
            raise
    
    def save_analysis_results(self):
        """Save analysis results to database"""
        try:
            # Save to PostgreSQL
            with self.postgres_engine.begin() as conn:
                for company_id, metrics in self.analysis_results.get('centrality_metrics', {}).items():
                    conn.execute(text("""
                        INSERT INTO network_analysis 
                        (analysis_date, analysis_type, company_id, centrality_metrics, relationship_metrics, financial_metrics, risk_assessment, recommendations)
                        VALUES (CURRENT_TIMESTAMP, 'comprehensive', :company_id, :centrality, :relationships, :financial, :risks, :recommendations)
                        ON CONFLICT (company_id, analysis_date) DO UPDATE SET
                        centrality_metrics = EXCLUDED.centrality_metrics,
                        relationship_metrics = EXCLUDED.relationship_metrics,
                        financial_metrics = EXCLUDED.financial_metrics,
                        risk_assessment = EXCLUDED.risk_assessment,
                        recommendations = EXCLUDED.recommendations
                    """), {
                        'company_id': company_id,
                        'centrality': json.dumps(metrics),
                        'relationships': json.dumps(self.analysis_results.get('relationship_patterns', {})),
                        'financial': json.dumps(self.analysis_results.get('financial_flows', {})),
                        'risks': json.dumps(self.analysis_results.get('risk_assessment', {})),
                        'recommendations': json.dumps(self.analysis_results.get('insights', {}))
                    })
            
            # Save to MongoDB
            network_analysis_collection = self.mongo_db.network_analysis
            analysis_doc = {
                'analysis_date': datetime.now(),
                'analysis_type': 'comprehensive',
                'results': self.analysis_results,
                'network_stats': {
                    'total_nodes': self.network_graph.number_of_nodes() if self.network_graph else 0,
                    'total_edges': self.network_graph.number_of_edges() if self.network_graph else 0,
                    'density': nx.density(self.network_graph) if self.network_graph else 0
                }
            }
            
            network_analysis_collection.insert_one(analysis_doc)
            
            logger.info("✅ Analysis results saved to database")
            
        except Exception as e:
            logger.error(f"❌ Saving analysis results failed: {e}")
            raise
    
    def run_complete_analysis(self):
        """Run complete network analysis"""
        try:
            logger.info("🔍 Starting comprehensive network analysis...")
            
            # Build network graph
            self.build_network_graph()
            
            # Run all analyses
            self.calculate_centrality_metrics()
            self.analyze_relationship_patterns()
            self.analyze_financial_flows()
            self.assess_risks()
            self.generate_insights()
            
            # Save results
            self.save_analysis_results()
            
            logger.info("✅ Comprehensive network analysis completed")
            
            return self.analysis_results
            
        except Exception as e:
            logger.error(f"❌ Complete analysis failed: {e}")
            raise

def main():
    """Main function to run network analysis"""
    try:
        # This would be called from the main application
        # For now, we'll just show the structure
        print("Network Analysis Engine Ready")
        print("Use this class to analyze the business network of all 29 companies")
        
    except Exception as e:
        logger.error(f"Network analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 