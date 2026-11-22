from confluent_kafka.admin import AdminClient, NewTopic

admin = AdminClient({"bootstrap.servers": "localhost:9092"})
for topico, f in admin.create_topics([NewTopic("mensagens", num_partitions=3, replication_factor=1)]).items():
    try:
        f.result()
        print(f"topico '{topico}' criado com 3 particoes")
    except Exception as e:
        print("aviso:", e)
