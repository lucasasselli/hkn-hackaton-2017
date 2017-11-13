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
    if len(temp) > 0:
        out.append(temp)

    return out


def user_has_tags(user, event_tags):
    user_tags = user.tags
    # Print it
    for utag in user_tags:
        for etag in event_tags:
            if etag == utag:
                return True

    return False
