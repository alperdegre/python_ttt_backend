
def test_read_main(client):
    response = client.get("/hello-world")
    assert response.status_code == 200
    assert response.json() == {"message":"Hello World"}