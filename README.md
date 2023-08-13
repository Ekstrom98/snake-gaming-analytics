# Snake Gaming Analytics

## 🚧 Work in Progress 🚧
This is a fun data engineering project currently under development. It's designed to be an end-to-end solution that bridges game development with data analytics.

## Description
The project revolves around a simple game of Snake that generates data. By playing the game, you generate data which is then sent to Apache Kafka. From there, subscribers can ingest the data, further process it, and derive various metrics. The end result? A [Streamlit dashboard](https://snake-gaming-analytics.streamlit.app/) showcasing gaming analytics. More fun metrics are being considered.

## Installation & Setup

### Prerequisites
- Docker
- Python 3.x

### Setup

1. **Clone the Repository**:
   ```
   git clone https://github.com/Ekstrom98/snake-gaming-analytics.git
   cd snake-gaming-analytics-main
   ```

2. **Set Up Python Environment**:
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Docker Setup**:
   ```
   docker-compose up -d
   ```

## Game Details

- **Play Snake**:
   ```
   python snake.py
   ```

## Data Flow & Processing

1. **Data from Snake Game to Apache Kafka**:
   Play the game and the data gets sent to Apache Kafka.

2. **Kafka to PostgreSQL Consumer**:
   ```
   python kafka_to_postgres_consumer.py
   ```

3. **Recreate Kafka Topics (if needed)**:
   ```
   python recreate_kafka_topics.py
   ```

4. **Some scripts for specific queries for the Database**:
   ```
   python query_database.py
   ```

## Visualization & Analytics

To view the gaming analytics, visit the Streamlit dashboard: [Snake Gaming Analytics Dashboard](https://snake-gaming-analytics.streamlit.app/)
