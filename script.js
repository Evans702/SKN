
async function sendRequest(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    const result = await response.json();

    if (!response.ok) {
        throw new Error(result.message || "操作失败");
    }

    return result;
}

function showMessage(id, message) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = message;
    }
}


// =========================
// 学生信息录入：page2.html
// 只录入姓名、专业、年级
// =========================

const studentForm = document.getElementById("studentForm");

if (studentForm) {
    studentForm.onsubmit = async function (event) {
        event.preventDefault();

        const name = document.getElementById("studentName").value.trim();
        const major = document.getElementById("studentMajor").value.trim();
        const grade = document.getElementById("studentGrade").value.trim();

        if (!name || !major || !grade) {
            alert("请填写姓名、专业和年级！");
            return;
        }

        try {
            const result = await sendRequest("/student", {
                name: name,
                major: major,
                grade: grade
            });

            showMessage("addResult", result.message || "学生信息录入成功！");
            studentForm.reset();
        } catch (error) {
            showMessage("addResult", "录入失败：" + error.message);
        }
    };
}


// =========================
// 学生信息查询：page1.html
// =========================

const btn3 = document.getElementById("btn3");

if (btn3) {
    btn3.onclick = async function () {
        const name = document.getElementById("queryName").value.trim();

        if (!name) {
            alert("请输入学生姓名！");
            return;
        }

        try {
            const response = await fetch(
                "/student/" + encodeURIComponent(name)
            );
            const data = await response.json();

            if (!response.ok) {
                showMessage("queryResult", data.message || "查询失败");
                return;
            }

            showMessage(
                "queryResult",
                `姓名：${data.name}；专业：${data.major || "暂无"}；` +
                `年级：${data.grade || "暂无"}`
            );
        } catch (error) {
            alert("查询失败：" + error.message);
        }
    };
}


// =========================
// 查询学生知识网络
// =========================


const networkBtn = document.getElementById("networkBtn");

if (networkBtn) {
    networkBtn.onclick = async function () {
        const name = document.getElementById("queryName").value.trim();

        if (!name) {
            alert("请先输入学生姓名！");
            return;
        }

        try {
            const response = await fetch(
                "/student/" + encodeURIComponent(name) + "/network"
            );
            const data = await response.json();

            if (!response.ok) {
                showMessage("networkResult", data.message || "查询失败");
                return;
            }

            if (!Array.isArray(data)) {
                showMessage("networkResult", data.message || "暂无关联数据");
                return;
            }

            const lines = data.map(item =>
                `${item.student} —[${item.relationship}]→ ` +
                `${item.node_type}：${item.node_name || "未命名"}`
            );

            showMessage("networkResult", lines.join("\n"));
        } catch (error) {
            showMessage("networkResult", "查询失败：" + error.message);
        }
    };
}


// =========================
// 业务动作一：学生加入团队
// =========================

const joinTeamBtn = document.getElementById("joinTeamBtn");

if (joinTeamBtn) {
    joinTeamBtn.onclick = async function () {
        const student = document.getElementById("joinStudent").value.trim();
        const team = document.getElementById("joinTeam").value.trim();

        if (!student || !team) {
            alert("请填写学生姓名和团队名称！");
            return;
        }

        try {
            const result = await sendRequest("/team/join", {
                student: student,
                team: team
            });

            showMessage("joinResult", result.message || "操作成功");
        } catch (error) {
            showMessage("joinResult", "操作失败：" + error.message);
        }
    };
}


// =========================
// 业务动作二：团队报名竞赛
// =========================


const registerBtn = document.getElementById("registerBtn");

if (registerBtn) {
    registerBtn.onclick = async function () {
        const team = document.getElementById("registerTeam").value.trim();
        const competition = document
            .getElementById("registerCompetition").value.trim();

        if (!team || !competition) {
            alert("请填写团队名称和竞赛名称！");
            return;
        }

        try {
            const result = await sendRequest("/team/register", {
                team: team,
                competition: competition
            });

            showMessage(
                "registerResult",
                result.message || "报名成功！"
            );
        } catch (error) {
            showMessage(
                "registerResult",
                "报名失败：" + error.message
            );
        }
    };
}
