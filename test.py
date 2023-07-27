def test_func(**kwargs):
    key = list(locals()["kwargs"].keys())[0]
    value = locals()["kwargs"][key]
    print(key, value)


if __name__ == "__main__":
    # test_func(params1="params1", params2="params2", params3="params3")
    test_func(params1="params1")