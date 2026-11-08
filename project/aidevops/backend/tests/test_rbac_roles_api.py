"""角色管理接口 /api/v1/roles 的 RBAC 与业务规则测试。"""


# ---------- 认证 ----------

def test_list_roles_requires_token(client):
    resp = client.get("/api/v1/roles")
    assert resp.status_code == 401
    assert resp.json()["code"] == 401


def test_list_roles_rejects_bad_token(client):
    resp = client.get("/api/v1/roles", headers={"Authorization": "Bearer not-a-jwt"})
    assert resp.status_code == 401


# ---------- 只读用户 ----------

def test_viewer_can_list_roles(client, users, auth):
    resp = client.get("/api/v1/roles", headers=auth(users.viewer))
    assert resp.status_code == 200
    body = resp.json()
    assert body["code"] == 0
    codes = {r["code"] for r in body["data"]}
    assert {"admin", "developer", "viewer"} <= codes


def test_viewer_cannot_create_role(client, users, auth):
    resp = client.post(
        "/api/v1/roles",
        headers=auth(users.viewer),
        json={"name": "x", "code": "x", "permissions": []},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == 403


def test_viewer_cannot_update_role(client, roles, users, auth):
    resp = client.put(
        f"/api/v1/roles/{roles.viewer.id}",
        headers=auth(users.viewer),
        json={"name": "新名称"},
    )
    assert resp.status_code == 403


def test_viewer_cannot_delete_role(client, roles, users, auth):
    resp = client.delete(
        f"/api/v1/roles/{roles.viewer.id}",
        headers=auth(users.viewer),
    )
    assert resp.status_code == 403


# ---------- 超级管理员：CRUD ----------

def test_admin_create_role_success(client, users, auth):
    payload = {
        "name": "审计员",
        "code": "auditor",
        "description": "只读审计",
        "permissions": ["user:read", "role:read"],
    }
    resp = client.post("/api/v1/roles", headers=auth(users.admin), json=payload)
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["code"] == "auditor"
    assert data["name"] == "审计员"
    assert data["permissions"] == ["user:read", "role:read"]
    assert data["is_default"] is False
    assert "created_at" in data


def test_admin_create_role_validation_error(client, users, auth):
    # code 为空字符串，不满足 min_length=1
    resp = client.post(
        "/api/v1/roles",
        headers=auth(users.admin),
        json={"name": "空编码", "code": "", "permissions": []},
    )
    assert resp.status_code == 422


def test_create_role_duplicate_code(client, roles, users, auth):
    resp = client.post(
        "/api/v1/roles",
        headers=auth(users.admin),
        json={"name": "另一个管理员", "code": "admin", "permissions": []},
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == 1000
    assert "编码" in resp.json()["msg"]


def test_create_role_duplicate_name(client, roles, users, auth):
    resp = client.post(
        "/api/v1/roles",
        headers=auth(users.admin),
        json={"name": "只读用户", "code": "viewer2", "permissions": []},
    )
    assert resp.status_code == 400
    assert "名称" in resp.json()["msg"]


def test_admin_update_role(client, roles, users, auth):
    resp = client.put(
        f"/api/v1/roles/{roles.viewer.id}",
        headers=auth(users.admin),
        json={"name": "只读访客", "permissions": ["user:read"]},
    )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["name"] == "只读访客"
    assert data["permissions"] == ["user:read"]
    # code 创建后不可修改（RoleUpdate 无 code 字段，序列化时忽略）
    assert data["code"] == "viewer"


def test_update_role_duplicate_name(client, roles, users, auth):
    resp = client.put(
        f"/api/v1/roles/{roles.viewer.id}",
        headers=auth(users.admin),
        json={"name": "开发人员"},
    )
    assert resp.status_code == 400


def test_update_nonexistent_role(client, users, auth):
    resp = client.put(
        "/api/v1/roles/9999",
        headers=auth(users.admin),
        json={"name": "幽灵"},
    )
    assert resp.status_code == 404
    assert resp.json()["code"] == 1000


# ---------- 删除约束 ----------

def test_cannot_delete_default_role(client, roles, users, auth):
    resp = client.delete(
        f"/api/v1/roles/{roles.admin.id}",
        headers=auth(users.admin),
    )
    assert resp.status_code == 400
    assert "默认角色" in resp.json()["msg"]


def test_cannot_delete_role_with_bound_users(client, roles, users, auth):
    # viewer1 绑定在 viewer 角色上
    resp = client.delete(
        f"/api/v1/roles/{roles.viewer.id}",
        headers=auth(users.admin),
    )
    assert resp.status_code == 400
    assert "用户" in resp.json()["msg"]


def test_delete_role_after_unbinding_user(client, roles, users, auth):
    # 先解绑用户，再删除角色应成功
    unbind = client.put(
        f"/api/v1/users/{users.viewer.id}",
        headers=auth(users.admin),
        json={"role_id": None},
    )
    assert unbind.status_code == 200

    resp = client.delete(
        f"/api/v1/roles/{roles.viewer.id}",
        headers=auth(users.admin),
    )
    assert resp.status_code == 200
    assert resp.json()["msg"] == "删除成功"


def test_delete_nonexistent_role(client, users, auth):
    resp = client.delete("/api/v1/roles/9999", headers=auth(users.admin))
    assert resp.status_code == 404


def test_admin_delete_custom_role(client, users, auth):
    create = client.post(
        "/api/v1/roles",
        headers=auth(users.admin),
        json={"name": "临时角色", "code": "temp", "permissions": []},
    )
    role_id = create.json()["data"]["id"]
    resp = client.delete(f"/api/v1/roles/{role_id}", headers=auth(users.admin))
    assert resp.status_code == 200
