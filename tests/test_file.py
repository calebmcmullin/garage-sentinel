from routes import file as file_route

def test_upload_missing_file(client, standard_user, login_user, test_database):
    user, _ = standard_user
    login_user(user)

    response = client.post('/api/file', follow_redirects=False)

    assert response.status_code == 422

def test_upload_invalid_file(client, standard_user, login_user, test_database):
    user, _ = standard_user
    login_user(user)

    response = client.post(
        '/api/file',
        files = {'file': ("malicious.exe", b"fake executable content", "application/octet-stream")},
        follow_redirects=False
    )

    assert response.status_code == 415

def test_upload_invalid_file_size(client, standard_user, login_user, test_database, monkeypatch):
    user, _ = standard_user
    login_user(user)

    monkeypatch.setattr(file_route, "MAX_FILE_SIZE", 1024)

    response = client.post(
        '/api/file',
        files = {'file': ("large.png", b"x" * 2048, "image/png")},
        follow_redirects=False
    )

    assert response.status_code == 413