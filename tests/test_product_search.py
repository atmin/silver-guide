import pytest

URL = "/api/v1/products/"


def skus(response):
    return {p["sku"] for p in response.json()["results"]}


@pytest.mark.django_db
class TestQueryFilter:
    def test_q_matches_title_substring_case_insensitive(self, api_client, products):
        response = api_client.get(URL, {"q": "млЯко"})
        assert response.status_code == 200
        assert skus(response) == {"PRD-001", "PRD-002"}

    def test_q_matches_sku_substring(self, api_client, products):
        response = api_client.get(URL, {"q": "SIR"})
        assert response.status_code == 200
        assert skus(response) == {"SIR-001", "SIR-002"}


@pytest.mark.django_db
class TestSkuFilter:
    def test_sku_exact_match_case_insensitive(self, api_client, products):
        response = api_client.get(URL, {"sku": "sir-001"})
        assert response.status_code == 200
        assert skus(response) == {"SIR-001"}

    def test_sku_no_partial_match(self, api_client, products):
        response = api_client.get(URL, {"sku": "SIR"})
        assert response.status_code == 200
        assert skus(response) == set()


@pytest.mark.django_db
class TestPriceFilter:
    def test_price_min_inclusive(self, api_client, products):
        response = api_client.get(URL, {"price_min": "3.99"})
        assert response.status_code == 200
        assert skus(response) == {"SIR-001", "SIR-002"}

    def test_price_max_inclusive(self, api_client, products):
        response = api_client.get(URL, {"price_max": "1.49"})
        assert response.status_code == 200
        assert skus(response) == {"PRD-002", "HRA-001"}

    def test_price_range(self, api_client, products):
        response = api_client.get(URL, {"price_min": "1.50", "price_max": "4.00"})
        assert response.status_code == 200
        assert skus(response) == {"PRD-001", "SIR-001"}


@pytest.mark.django_db
class TestCategoryFilter:
    def test_category_id_exact_category(self, api_client, products, category_tree):
        grandchild = category_tree["grandchild"]
        response = api_client.get(URL, {"category_id": grandchild.id})
        assert response.status_code == 200
        assert skus(response) == {"SIR-001", "SIR-002"}

    def test_category_id_includes_descendants(
        self, api_client, products, category_tree
    ):
        root = category_tree["root"]
        response = api_client.get(URL, {"category_id": root.id})
        assert response.status_code == 200
        assert skus(response) == {"PRD-001", "PRD-002", "SIR-001", "SIR-002", "HRA-001"}

    def test_category_slug_exact_category(self, api_client, products):
        response = api_client.get(URL, {"category_slug": "hrani-mlechni-sirena"})
        assert response.status_code == 200
        assert skus(response) == {"SIR-001", "SIR-002"}

    def test_category_slug_includes_descendants(self, api_client, products):
        response = api_client.get(URL, {"category_slug": "hrani-mlechni"})
        assert response.status_code == 200
        assert skus(response) == {"PRD-001", "PRD-002", "SIR-001", "SIR-002"}

    def test_category_slug_unknown_returns_404(self, api_client, products):
        response = api_client.get(URL, {"category_slug": "does-not-exist"})
        assert response.status_code == 404

    def test_category_id_unknown_returns_404(self, api_client, products):
        response = api_client.get(URL, {"category_id": 99999})
        assert response.status_code == 404


@pytest.mark.django_db
class TestCombinedFilters:
    def test_category_and_price_max(self, api_client, products, category_tree):
        child = category_tree["child"]
        response = api_client.get(URL, {"category_id": child.id, "price_max": "1.50"})
        assert response.status_code == 200
        assert skus(response) == {"PRD-002"}

    def test_q_and_price_range(self, api_client, products):
        response = api_client.get(URL, {"q": "сирене", "price_max": "4.00"})
        assert response.status_code == 200
        assert skus(response) == {"SIR-001"}


@pytest.mark.django_db
class TestInactiveProducts:
    def test_inactive_never_appears_in_list(self, api_client, products):
        response = api_client.get(URL)
        assert response.status_code == 200
        assert "HRA-INACTIVE" not in skus(response)

    def test_inactive_excluded_from_category_filter(
        self, api_client, products, category_tree
    ):
        root = category_tree["root"]
        response = api_client.get(URL, {"category_id": root.id})
        assert response.status_code == 200
        assert "HRA-INACTIVE" not in skus(response)

    def test_inactive_excluded_from_q_filter(self, api_client, products):
        response = api_client.get(URL, {"q": "Стар"})
        assert response.status_code == 200
        assert skus(response) == set()


@pytest.mark.django_db
class TestUnknownFilterParam:
    def test_unknown_param_returns_400(self, api_client, products):
        response = api_client.get(URL, {"category": "1"})
        assert response.status_code == 400
