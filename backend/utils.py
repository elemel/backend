def flatten(iterables):
    for iterable in iterables:
        for item in iterable:
            yield item
