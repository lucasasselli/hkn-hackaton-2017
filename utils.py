def group(lst, n):
    i = 0
    out = list()
    temp = list()
    for elem in lst:
        temp.append(elem)
        i += 1
        if i == 3:
            i = 0
            out.append(temp)
            temp = list()

    return out


def user_has_tags(user, tags):
    # TODO
    return True
