def test_func(**kwargs):
    for key, value in kwargs.items():
        print(key, value)


if __name__ == "__main__":
    test_func(params1="params1", params2="params2", params3="params3")