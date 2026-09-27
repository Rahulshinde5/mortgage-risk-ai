# AI-Powered Mortgage Lending & Credit Risk Intelligence Platform

An automated fintech analytics platform that combines public CFPB mortgage data, Python-based data engineering, DuckDB analytics, Streamlit dashboards, and a Claude-powered AI analytical agent.

The platform helps analytics and business teams monitor mortgage lending activity, delinquency trends, borrower credit-risk composition, and changes in key market indicators.

## Business Problem

Mortgage lending teams need to monitor multiple indicators at the same time:

- Mortgage origination activity
- Origination dollar volume
- Early-stage delinquency
- Serious delinquency
- Borrower credit-score composition
- Higher-risk borrower share
- Average mortgage size

This project automates the data preparation and KPI workflow and adds a natural-language AI analysis layer.

## Solution Architecture

```text
CFPB Public Data
       |
       v
Python / Requests
       |
       v
Data Transformation & Validation
       |
       v
KPI Generation
       |
       v
DuckDB Analytical Layer
       |
       v
Streamlit Dashboard
       |
       v
Claude AI Analytical Agent
       |
       v
Python / DuckDB Analytical Tools
       |
       v
Business Explanation