def search_for_errors(ty_bags, errors):
    for key, value in ty_bags.vars.items():
        if len(value) > 1:
            errors.append(
                "Can't infer type of: '" + str(key) + "', between" + str(sorted(value))
            )
    for key, child in ty_bags.children.items():
        search_for_errors(child, errors)
