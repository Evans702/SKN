from flask import Flask, jsonify, request, send_from_directory
from neo4j import GraphDatabase
from pathlib import Path

app = Flask(__name__)

#  Neo4j 实例的连接信息
URI = "bolt://52.23.232.187:7687"
USERNAME = "neo4j"
PASSWORD = "history-algorithm-passengers"

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

# 前端文件夹
WEB_DIR = Path(__file__).resolve().parent.parent / "frontend"


# =========================
# 网页和静态文件
# =========================

@app.route("/")
def home():
    return send_from_directory(WEB_DIR, "index.html")


@app.route("/<path:filename>")
def web_files(filename):
    return send_from_directory(WEB_DIR, filename)


# =========================
# 学生信息录入
# =========================


@app.route("/student", methods=["POST"])
def add_student():
    data = request.get_json()

    name = data.get("name", "").strip()
    major = data.get("major", "").strip()
    grade = data.get("grade", "").strip()

    if not name or not major or not grade:
        return {"message": "请填写姓名、专业和年级"}, 400

    with driver.session() as session:
        session.run(
            """
            MERGE (s:Student {name: $name})
            SET s.major = $major,
                s.grade = $grade
            """,
            name=name,
            major=major,
            grade=grade
        )

    return {"message": "学生信息录入成功"}


# =========================
# 学生信息查询
# =========================

@app.route("/student/<name>")
def get_student(name):
    with driver.session() as session:
        record = session.run(
            """
            MATCH (s:Student {name: $name})
            RETURN s.name AS name,
                   s.major AS major,
                   s.grade AS grade
            """,
            name=name
        ).single()

    if record is None:
        return jsonify({"message": "没有找到这个学生"}), 404

    return jsonify(dict(record))


# =========================
# 学生知识网络查询
# =========================


RELATIONSHIP_TRANSLATIONS = {
    "TEAM_MEMBER_OF": "加入团队",
    "MEMBER_OF": "成员",
    "INTERESTED_IN": "兴趣方向",
    "ENROLLED_IN": "已报名",
    "ATTENDS": "参加",
    "REGISTERS_FOR": "报名竞赛",
    "STUDIED_IN": "学习于",
    "LEARNS": "学习",
    "TAUGHT_BY": "由…教授",
    "IN": "属于",
    "KNOWS": "认识",
    "FOLLOWS": "关注",
    "WORKS_WITH": "合作",
    "CREATED": "创建",
    "OFFERS": "提供"
}


@app.route("/student/<name>/network", methods=["GET"])
def get_student_network(name):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (s:Student {name: $name})
            OPTIONAL MATCH (s)-[r]-(n)
            RETURN s.name AS student,
                   type(r) AS relationship,
                   labels(n)[0] AS node_type,
                   n.name AS node_name
            """,
            name=name
        )
        records = [dict(record) for record in result]

    if not records:
        return {"message": "该同学不存在"}, 404

    nodes = {}
    edges = []

    student_id = name
    nodes[student_id] = {
        "id": student_id,
        "label": student_id,
        "color": "#7ec8ff",
        "shape": "dot"
    }

    for row in records:
        rel = row.get("relationship")
        if rel is None:
            continue

        node_name = row.get("node_name") or row.get("node_type") or "未知"
        node_type = row.get("node_type") or "Unknown"
        translated_rel = RELATIONSHIP_TRANSLATIONS.get(rel, rel)

        node_id = f"{node_type}:{node_name}"

        if node_id not in nodes:
            nodes[node_id] = {
                "id": node_id,
                "label": node_name,
                "color": "#bdf2bd",
                "shape": "dot"
            }

        edges.append({
            "from": student_id,
            "to": node_id,
            "label": translated_rel,
            "arrows": "to"
        })

    return {"nodes": list(nodes.values()), "edges": edges}



# =========================
# 业务动作一：学生加入团队
# =========================

@app.route("/team/join", methods=["POST"])
def join_team():
    data = request.get_json() or {}

    student = data.get("student", "").strip()
    team = data.get("team", "").strip()

    if not student or not team:
        return {"message": "请填写学生姓名和团队名称"}, 400

    with driver.session() as session:
        result = session.run(
            """
            MATCH (s:Student {name: $student})
            MATCH (t:Team {name: $team})
            MERGE (s)-[r:TEAM_MEMBER_OF]->(t)
            RETURN s.name AS student, t.name AS team
            """,
            student=student,
            team=team
        )
        record = result.single()

    if record is None:
        return {
            "message": "加入失败：请检查学生姓名和团队名称是否存在"
        }, 404

    return {
        "message": f"{record['student']} 已成功加入 {record['team']}"
    }
# =========================
# 业务动作二：团队报名竞赛
# =========================

@app.route("/team/register", methods=["POST"])
def register_team():
    data = request.get_json() or {}

    team = data.get("team", "").strip()
    competition = data.get("competition", "").strip()

    if not team or not competition:
        return {"message": "请填写团队名称和竞赛名称"}, 400

    with driver.session() as session:
        result = session.run(
            """
            MATCH (t:Team {name: $team})
            MATCH (c:Competition {name: $competition})
            MERGE (t)-[r:REGISTERS_FOR]->(c)
            RETURN t.name AS team,
                   c.name AS competition
            """,
            team=team,
            competition=competition
        )

        record = result.single()

    if record is None:
        return {
            "message": "报名失败：请检查团队名称和竞赛名称是否存在"
        }, 404

    return {
        "message": f"{record['team']} 已成功报名 {record['competition']}"
    }




if __name__ == "__main__":
    app.run(debug=True)
