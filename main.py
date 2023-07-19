import requests


def test_req() -> None:
    ''' send email '''
    url = "https://bankrot.gov.by/"
    resp = requests.get(url=url)
    print(resp.text)


if __name__ == "__main__":
    test_req()