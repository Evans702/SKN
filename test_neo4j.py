from neo4j import GraphDatabase

URI = " "
USERNAME = "neo4j"
PASSWORD = " "

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

driver.verify_connectivity()

with driver.session() as session:
    result = session.run(
        """
        MATCH (s:student {name:"张三"})
        RETURN s.name AS name, s.major AS major
        """
    )

    for record in result:
        print("姓名：", record["name"])
        print("专业：", record["major"])


driver.close()