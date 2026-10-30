def test_get_tasks_returns_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Learn Docker",
            "description": "Practice Docker commands",
            "completed": False,
        },
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Learn Docker"
    assert response.json()["completed"] is False


def test_get_task_by_id(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Learn Python"},
    )
    task_id = create_response.json()["id"]

    response = client.get(f"/tasks/{task_id}")

    assert response.status_code == 200
    assert response.json()["title"] == "Learn Python"


def test_update_task(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Original title"},
    )
    task_id = create_response.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"completed": True},
    )

    assert response.status_code == 200
    assert response.json()["completed"] is True


def test_delete_task(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Task to delete"},
    )
    task_id = create_response.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404


def test_create_task_without_title_returns_422(client):
    response = client.post(
        "/tasks",
        json={"description": "A task without a title"},
    )
    assert response.status_code == 422
