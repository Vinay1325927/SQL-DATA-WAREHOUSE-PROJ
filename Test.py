def test_ownership_rule(client):
    """
    GIVEN a joke submitted by one user
    WHEN a different logged-in user tries to update that joke
    THEN 403 OWNERSHIP_RULE is returned and the joke remains unchanged

    LEVEL: EDGE
    """
    original_text = (
        "Scientists tried to cross a cheetah and a crab, but stopped "
        "when they realized it could go sideways really fast."
    )
    replacement_text = "This update should be rejected."

    owner = {
        "username": "owner",
        "password": "ownerpass123",
    }
    other_user = {
        "username": "otheruser",
        "password": "otherpass123",
    }

    # Given: the owner creates a joke.
    assert client.post("/auth/register", json=owner).status_code == 201
    assert client.post("/auth/login", json=owner).status_code == 200
    assert (
        client.post("/jokes", json={"text": original_text}).status_code
        == 201
    )
    assert client.post("/auth/logout").status_code == 200

    # When: another user attempts to update the owner's joke.
    assert client.post(
        "/auth/register",
        json=other_user,
    ).status_code == 201
    assert client.post(
        "/auth/login",
        json=other_user,
    ).status_code == 200

    response = client.put(
        "/jokes/1",
        json={"text": replacement_text},
    )

    # Then: the ownership rule refuses the update.
    assert response.status_code == 403
    data = response.get_json()
    assert data["error"]["code"] == "OWNERSHIP_RULE"
    assert data["error"]["message"] == "You can only edit your own joke."

    # Confirm that the owner's original text was not changed.
    assert client.post("/auth/logout").status_code == 200
    assert client.post("/auth/login", json=owner).status_code == 200

    ledger_response = client.get("/jokes")
    assert ledger_response.status_code == 200

    jokes = ledger_response.get_json()["data"]["jokes"]
    joke_texts = [joke["text"] for joke in jokes]

    assert original_text in joke_texts
    assert replacement_text not in joke_texts
