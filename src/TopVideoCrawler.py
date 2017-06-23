# -*- coding: utf-8 -*-

import urllib2, math, time, json, os

def getShowList(outpath, cid = '4fa043e1446bdf29', cat = '电视剧', orderby = 'view-count', count = 50, maxcount = 1200):
    # Linux -> UTF-8    Windows -> GBK
    fd = open(outpath + 'showlist_' + cat.decode("utf-8") + '_' + time.strftime("%Y-%m-%d", time.localtime()) + '.txt', 'w')
    getShowURL = 'https://openapi.youku.com/v2/shows/by_category.json'
    cidStr = 'client_id=' + cid
    catStr = 'category=' + cat
    orderbyStr = 'orderby=' + orderby
    countStr = 'count=' + str(count)
    # i is the cur page num
    for i in range(1, int(math.ceil(maxcount / count)) + 1):
        pageStr = 'page=' + str(i)
        finalURL = getShowURL + '?' + cidStr + '&' + catStr +  '&' + orderbyStr +  '&' + countStr +  '&' + pageStr
        #pageFd = open(outpath + 'showlist_' + cat.decode("utf-8") + '_' + str(count) + '_%03d' % (i) + '.txt', 'w')
        while True:
            try:
                print('Querying ' + finalURL)
                resFd = urllib2.urlopen(finalURL, timeout = 15)
                res = resFd.read()
            except urllib2.HTTPError as e:
                print(str(e))
                print(e.read())
                print('Retrying...')
            except urllib2.URLError as e:
                print(str(e))
                print('Retrying...')
            except Exception as e:
                print(str(e))
                print('Retrying...')
            else:
                #pageFd.write(res)
                fd.write(res + '\n')
                print('Success')
                break
        #pageFd.close()
    fd.close()

def getVideoList(infile, outpath, cid = '4fa043e1446bdf29', count = 50):
    videoListFd = open(outpath + 'videolist_' + infile.decode('utf-8')[infile.decode('utf-8').find('showlist_') + len('showlist_'):], 'w')
    showListFd = open(infile.decode('utf-8'), 'r')
    getVideoURL = 'https://openapi.youku.com/v2/shows/videos.json'
    cidStr = 'client_id=' + cid
    countStr = 'count=' + str(count)
    qNum = 1
    for line in showListFd.readlines():
        showJson = json.loads(line)
        for showEntry in showJson['shows']:
            # get videos in each show
            sidStr = 'show_id=' + showEntry['id']
            pageNum = 1
            tryNum = 1
            while True:
                if 0 == tryNum % 10:
                    time.sleep(60)
                try:
                    pageStr = 'page=' + str(pageNum)
                    finalURL = getVideoURL + '?' + cidStr + '&' + sidStr + '&' + countStr + '&' + pageStr
                    print('Querying NO.' + str(qNum) + ' ' +  finalURL)
                    resFd = urllib2.urlopen(finalURL, timeout = 15)
                    res = resFd.read()
                except urllib2.HTTPError as e:
                    print(str(e))
                    print(e.read())
                    print('Retrying...')
                    tryNum = tryNum + 1
                except urllib2.URLError as e:
                    print(str(e))
                    print('Retrying...')
                    tryNum = tryNum + 1
                except Exception as e:
                    print(str(e))
                    print('Retrying...')
                    tryNum = tryNum + 1
                else:
                    videoListFd.write(showEntry['id'] + '\t' + res + '\n')
                    print('Success')
                    if count * pageNum >= int(json.loads(res)['total']):
                        qNum = qNum + 1
                        break
                    else:
                        pageNum = pageNum + 1
    showListFd.close()
    videoListFd.close()         

def getVidUrlList(infile, outpath):
    vidurlFd = open(outpath + 'vid_url_' + infile.decode('utf-8')[infile.decode('utf-8').find('videolist_') + len('videolist_'):], 'w')
    videoListFd = open(infile.decode('utf-8'), 'r')
    videoNum = 0
    for line in videoListFd.readlines():
        videoJson = json.loads(line.split('\t', -1)[1])
        videoNum = videoNum + int(len(videoJson['videos']))
        for videoEntry in videoJson['videos']:
            vidurlFd.write(videoEntry['id'] + '\t' + videoEntry['link'] + '\n')
    print('Total ' + str(videoNum) + ' Videos')
    videoListFd.close()
    vidurlFd.close()

def getVideoMetadata(infile, outpath, cid = '4fa043e1446bdf29'):
    videoMetadataFd = open(outpath + 'video_metadata_' + infile.decode('utf-8')[infile.decode('utf-8').find('vid_url_') + len('vid_url_'):], 'w')
    vidurlFd = open(infile.decode('utf-8'), 'r')
    getVideoMetadataURL = 'https://openapi.youku.com/v2/videos/show_batch.json'
    cidStr = 'client_id=' + cid
    vid50List = []
    vid50Str = ''
    qNum = 1
    for line in vidurlFd.readlines():
        vid50List.append(line.split('\t')[0])
        if 50 == len(vid50List):
            vid50Str = vid50List[0]
            for vid in vid50List[1:]:
                vid50Str = vid50Str + ',' + vid
            #videoMetadataFd.write(vid50Str + '\n')
            # send request here
            tryNum = 1
            while True:
                if 0 == tryNum % 10:
                    time.sleep(60)
                try:
                    vidsStr = 'video_ids=' + vid50Str
                    finalURL = getVideoMetadataURL + '?' + cidStr + '&' + vidsStr
                    print('Querying NO.' + str((qNum - 1) * 50 + 1) + '-' + str(qNum * 50) + ' ' +  finalURL)
                    resFd = urllib2.urlopen(finalURL, timeout = 15)
                    res = resFd.read()
                except urllib2.HTTPError as e:
                    print(str(e))
                    print(e.read())
                    print('Retrying...')
                    tryNum = tryNum + 1
                except urllib2.URLError as e:
                    print(str(e))
                    print('Retrying...')
                    tryNum = tryNum + 1
                except Exception as e:
                    print(str(e))
                    print('Retrying...')
                    tryNum = tryNum + 1
                else:
                    videoMetadataFd.write(res + '\n')
                    print('Success')
                    qNum = qNum + 1
                    break
            vid50List = []
    if 0 != len(vid50List):
        vid50Str = vid50List[0]
        for vid in vid50List[1:]:
            vid50Str = vid50Str + ',' + vid
        #videoMetadataFd.write(vid50Str + '\n')
        # send request here
        tryNum = 1
        while True:
            if 0 == tryNum % 10:
                time.sleep(60)
            try:
                vidsStr = 'video_ids=' + vid50Str
                finalURL = getVideoMetadataURL + '?' + cidStr + '&' + vidsStr
                print('Querying NO.' + str((qNum - 1) * 50 + 1) + '-' + str((qNum - 1) * 50 + len(vid50List)) + ' ' +  finalURL)
                resFd = urllib2.urlopen(finalURL, timeout = 15)
                res = resFd.read()
            except urllib2.HTTPError as e:
                print(str(e))
                print(e.read())
                print('Retrying...')
                tryNum = tryNum + 1
            except urllib2.URLError as e:
                print(str(e))
                print('Retrying...')
                tryNum = tryNum + 1
            except Exception as e:
                print(str(e))
                print('Retrying...')
                tryNum = tryNum + 1
            else:
                videoMetadataFd.write(res + '\n')
                print('Success')
                qNum = qNum + 1
                break
        vid50List = []
    vidurlFd.close()
    videoMetadataFd.close()

def getUserList(infile, outpath):
    uidListFd = open(outpath + 'userlist_' + infile.decode('utf-8')[infile.decode('utf-8').find('metadata_') + len('metadata_'):], 'w')
    videoMetadataFd = open(infile.decode('utf-8'), 'r')
    userList = set()
    videoNum = 0
    for line in videoMetadataFd.readlines():
        videoJson = json.loads(line)
        for videoEntry in videoJson['videos']:
            if False == (videoEntry['user']['id'] in userList):
                userList.add(videoEntry['user']['id'])
            videoNum = videoNum + 1
    for uid in userList:
        uidListFd.write(uid + '\n')
    print('Total ' + str(videoNum) + ' Videos by ' + str(len(userList)) + ' Users')
    videoMetadataFd.close()
    uidListFd.close()
    
def getUserMetadata(infile, outpath, cid = '4fa043e1446bdf29'):
    userMetadataFd = open(outpath + 'user_metadata_' + infile.decode('utf-8')[infile.decode('utf-8').find('userlist_') + len('userlist_'):], 'w')
    uidListFd = open(infile.decode('utf-8'), 'r')
    getUserMetadataURL = 'https://openapi.youku.com/v2/users/show.json'
    cidStr = 'client_id=' + cid
    qNum = 1
    for uid in uidListFd.readlines():
        uidStr = 'user_id=' + uid.strip()
        tryNum = 1
        while True:
            if 0 == tryNum % 10:
                time.sleep(60)
            try:
                finalURL = getUserMetadataURL + '?' + cidStr + '&' + uidStr
                print('Querying NO.' + str(qNum) + ' ' + finalURL)
                resFd = urllib2.urlopen(finalURL, timeout = 15)
                res = resFd.read()
            except urllib2.HTTPError as e:
                print(str(e))
                print(e.read())
                print('Retrying...')
                tryNum = tryNum + 1
            except urllib2.URLError as e:
                print(str(e))
                print('Retrying...')
                tryNum = tryNum + 1
            except Exception as e:
                print(str(e))
                print('Retrying...')
                tryNum = tryNum + 1
            else:
                userMetadataFd.write(res + '\n')
                print('Success')
                qNum = qNum + 1
                break
    uidListFd.close()
    userMetadataFd.close()
    
def getHtml(infile, outpath):
    vidurlFd = open(infile.decode('utf-8'), 'r')
    getHtmlURL= 'http://index.youku.com/vr_keyword/id_'
    qNum = 1
    curPath = ''
    for line in vidurlFd.readlines():
        # mkdir for every 1000 entries, start by 1
        if 1 == qNum % 1000:
            curPath = outpath + str(qNum) + '-' + str(qNum + 1000 -1) + '/'
            os.mkdir(curPath.decode('utf-8'))
        tryNum = 1
        while True:
            if 0 == tryNum % 10:
                time.sleep(60)
            try:
                fields = line.split('\t', -1)
                finalURL = getHtmlURL + fields[1].strip()
                print('Querying NO.' + str(qNum) + ' ' + finalURL)
                resFd = urllib2.urlopen(finalURL, timeout = 15)
                res = resFd.read()
            except urllib2.HTTPError as e:
                print(str(e))
                print(e.read())
                print('Retrying...')
                tryNum = tryNum + 1
            except urllib2.URLError as e:
                print(str(e))
                print('Retrying...')
                tryNum = tryNum + 1
            except Exception as e:
                print(str(e))
                print('Retrying...')
                tryNum = tryNum + 1
            else:
                htmlFd = open(curPath.decode('utf-8') + fields[0] + '.html', 'w')
                htmlFd.write(res + '\n')
                htmlFd.close()
                print('Success')
                qNum = qNum + 1
                break
    vidurlFd.close()

def getViewCount(inpath, outfile, errfile):
    outFd = open(outfile, 'w')
    errFd = open(errfile, 'w')
    
    fileNum = 1
    # get subpath list
    subpathList = os.listdir(inpath.decode('UTF-8'))
    # for each subpath
    for sub in subpathList:
        curPath = inpath + str(sub) + '/'
        # get file list
        fileList = os.listdir(curPath.decode('UTF-8'))
        # for each file
        for f in fileList:
            curFile = curPath + str(f)
            print('Processing NO. ' + str(fileNum) + ' File')
            fileNum = fileNum + 1
            fd = open(curFile.decode('utf-8'), 'r')
            getVcFlag = False
            notFoundFlag = False
            notLongFlag = False
            for line in fd.readlines():
                if -1 != line.find('var youkuData'):
                    vcStr = eval(line[line.index('{') : line.rindex('}') + 1])
                    if 30 > len(vcStr['vv'][2]):
                        notLongFlag = True
                        break
                    # get view counts
                    getVcFlag = True
                    outFd.write(f[1:f.index('.')])
                    for i in range(len(vcStr['vv'][2]) - 1, len(vcStr['vv'][2]) - 1 - 30, -1):
                        outFd.write('\t' + vcStr['vv'][2][i])
                    outFd.write('\n')
                if -1 != line.find('没有找到相关指数信息'):
                    notFoundFlag = True
            if False == getVcFlag:
                if True == notFoundFlag:
                    errFd.write(f[1:f.index('.')] + '\tNot Found\n')
                elif True == notLongFlag:
                    errFd.write(f[1:f.index('.')] + '\tNot Long Enough\n')
                else:
                    errFd.write(f[1:f.index('.')] + '\tUnknown Reason\n')
            fd.close()
    
    outFd.close()
    errFd.close()

def test():
    print('All Done!')

if __name__ == '__main__':
    #getShowList(outpath = 'F:/Hot_Video_Collection/')
    #getShowList(outpath = 'F:/Hot_Video_Collection/', cat = '综艺')
    #getVideoList('F:/Hot_Video_Collection/showlist_电视剧_2015-12-22.txt', 'F:/Hot_Video_Collection/')
    #getVideoList('F:/Hot_Video_Collection/showlist_综艺_2015-12-22.txt', 'F:/Hot_Video_Collection/')
    #getVidUrlList('F:/Hot_Video_Collection/videolist_电视剧_2015-12-22.txt', 'F:/Hot_Video_Collection/')
    #getVidUrlList('F:/Hot_Video_Collection/videolist_综艺_2015-12-22.txt', 'F:/Hot_Video_Collection/')
    #getVideoMetadata('F:/Hot_Video_Collection/vid_url_电视剧_2015-12-22.txt', 'F:/Hot_Video_Collection/Metadata/')
    #getVideoMetadata('F:/Hot_Video_Collection/vid_url_综艺_2015-12-22.txt', 'F:/Hot_Video_Collection/Metadata/')
    #getUserList('F:/Hot_Video_Collection/video_metadata_电视剧_2015-12-22.txt', 'F:/Hot_Video_Collection/')
    #getUserList('F:/Hot_Video_Collection/video_metadata_综艺_2015-12-22.txt', 'F:/Hot_Video_Collection/')
    #getUserMetadata('F:/Hot_Video_Collection/userlist_电视剧_2015-12-22.txt', 'F:/Hot_Video_Collection/Metadata/')
    #getUserMetadata('F:/Hot_Video_Collection/userlist_综艺_2015-12-22.txt', 'F:/Hot_Video_Collection/Metadata/')
    #getHtml('F:/Hot_Video_Collection/vid_url_电视剧_2015-12-22.txt', 'F:/Hot_Video_Collection/HTML/')
    #getHtml('F:/Hot_Video_Collection/vid_url_综艺_2015-12-22.txt', 'F:/Hot_Video_Collection/HTML/')
    getViewCount('F:/Hot_Video_Collection/HTML/电视剧/', 
                 'F:/Hot_Video_Collection/ViewCount/out', 
                 'F:/Hot_Video_Collection/ViewCount/err')
    test()
    