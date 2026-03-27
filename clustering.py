from sklearn.cluster import DBSCAN

def cluster(data):
    if not data:
        return []
    return DBSCAN().fit_predict(data)
