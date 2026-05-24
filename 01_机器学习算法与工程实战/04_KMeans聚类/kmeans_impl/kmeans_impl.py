import numpy as np
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer


def distCos(vecA, vecB):
    return np.dot(vecA, vecB) / (np.sqrt(np.sum(np.square(vecA))) * np.sqrt(np.sum(np.square(vecB))))


def distEclud(vecA, vecB):
    return np.sqrt(np.sum(np.power(vecA - vecB, 2)))


def randCent(dataSet, k):
    m, n = dataSet.shape[0], dataSet.shape[1]
    index_list = list(range(m))
    np.random.shuffle(index_list)
    centroids = dataSet[index_list][:k]
    return centroids


def kMeans(dataSet, k, disMeans=distEclud, createCent=randCent):
    m = dataSet.shape[0]
    # 存放样本属于哪个类别以及到中心点的距离
    clusterAssment = np.zeros((m, 2))
    # 1, init k 中心点
    centroids = createCent(dataSet, k)
    clusterChanged = True
    while clusterChanged:
        clusterChanged = False
        # 2, E-Step 把每一个数据点划分到离它最近的中心点所属类别
        for i in range(m):
            minDist = float('inf')
            minIndex = -1
            for j in range(k):
                distJI = disMeans(centroids[j, :], dataSet[i, :])
                if distJI < minDist:
                    minDist = distJI
                    # 如果第i个数据点到第j个中心点更近，将i样本划分到第j类
                    minIndex = j
            if clusterAssment[i, 0] != minIndex:
                clusterChanged = True
            clusterAssment[i, :] = minIndex, minDist**2
        print(centroids)

        # 3, M-Step 更新μ1到μk，重新计算中心点坐标
        for cent in range(k):
            ptsInClust = dataSet[np.nonzero(clusterAssment[:, 0] == cent)]
            centroids[cent, :] = np.mean(ptsInClust, axis=0)
    return centroids, clusterAssment


if __name__ == '__main__':
    doc1 = '我爱北京北京天安门'
    doc2 = '我爱北京颐和园'
    doc3 = '欧洲杯意大利夺冠了'
    corpus = [doc1, doc2, doc3]
    corpus = [' '.join(list(jieba.cut(doc))) for doc in corpus]

    X = TfidfVectorizer().fit_transform(corpus)
    # print(type(X))

    result = kMeans(X.A, k=2, disMeans=distCos)
    print(result)
