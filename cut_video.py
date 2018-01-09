#!/usr/bin python
# -*- coding:utf-8 -*-

import os
import re
import subprocess
import logging  
import logging.handlers 

class cutVideo:
    def __init__(self,ipath,opath,hvd,tvd):
        self.ipath = ipath
        self.opath = opath
        self.hvd = hvd
        self.tvd = tvd

        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler("cut_video.log")
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)

        self.logger.addHandler(handler)
        self.logger.addHandler(console)

    def get_video_duration(self,fp):
        child = subprocess.Popen(['/usr/local/bin/ffmpeg','-i',fp],stdout=subprocess.PIPE,stderr=subprocess.PIPE) 
        err = child.stderr.read()
        child.stderr.close()
        p = r"(?<=Duration:).+?(?=,)"
        pattern = re.compile(p)
        matcher = re.search(pattern,err)
        if matcher:
            t = matcher.group(0).strip()
            sl = t.split('.')[0].split(':')
            h = int(sl[0])
            m = int(sl[1])
            s = int(sl[2])
            r = h * 60 * 60 + m * 60 + s
            return r
        else:
            return 0

    def cut_video_seg(self,ss,t,ifile,ofile):
        proc = subprocess.Popen(['/usr/local/bin/ffmpeg',
            '-ss',ss,
            '-t',t,
            '-accurate_seek',
            '-i',ifile,
            '-codec','copy',
            '-avoid_negative_ts','1',
            ofile],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout_value = proc.communicate()
        if os.path.exists(ofile) == False:
            self.logger.error('cut log:'+ stdout_value)
            return False
        else: 
            return True

    def cut_video_file(self,fn):
        self.logger.debug('************************************')
        self.logger.debug('file name:' + fn)
        fp = self.ipath + '/' + fn
        gfp = self.opath + '/' + fn 
        tfp = self.opath + '/' + fn.split('.mp4')[0] + '_temp.mp4'

        if hvd > -1 :
            self.logger.debug('start cut head')
            duration = self.get_video_duration(fp)
            self.logger.debug('duration:'+str(duration))
            ss = str(self.hvd)
            t = str(duration - self.hvd)
            r = self.cut_video_seg(ss,t,fp,tfp)
            if r :
                self.logger.debug('cut head status:success')
            else:
                self.logger.error('cut head status:failture')
                return

        if tvd > -1 :
            if hvd > -1 :
                self.logger.debug('start cut tail with temp')
                if os.path.exists(tfp):
                    # cut tail from temp file
                    duration = self.get_video_duration(tfp)
                    self.logger.debug('duration:'+str(duration))
                    ss = '0'
                    t = str(duration - self.tvd)
                    r = self.cut_video_seg(ss,t,tfp,gfp)
                    if r :
                        self.logger.debug('cut tail status(with temp):success')
                    else:
                        self.logger.error('cut tail status(with temp):failture')
                    
                    os.remove(tfp)
                else:
                    # cut head failture del temp file and exit
                    self.logger.warn('the head is failture,not cut tail of this video')
            else:
                # cut tail from old file
                self.logger.debug('start cut tail without temp')
                duration = self.get_video_duration(fp)
                self.logger.debug('duration:'+str(duration))
                ss = '0'
                t = str(duration - self.tvd)
                r = self.cut_video_seg(ss,t,fp,gfp)
                if r :
                    self.logger.debug('cut tail status(without temp):success')
                else:
                    self.logger.error('cut tail status(without temp):failture')

    def start(self):
        self.logger.debug('Start......................')
        self.logger.debug('input dir='+self.ipath)
        self.logger.debug('output dir='+self.opath)
        self.logger.debug('hvd='+str(self.hvd))
        self.logger.debug('tvd='+str(self.tvd))
        flist = os.listdir(self.ipath)
        for i in range(0,len(flist)):
            fn = flist[i] 
            fp = os.path.join(self.ipath,fn)
            if os.path.isfile(fp) and fp.endswith('.mp4'):
                self.cut_video_file(fn)
        self.logger.debug('End......................')

if __name__ == '__main__':
    ipath = raw_input("input the path of videos dir: ")
    opath = raw_input("input the path of output dir: ")
    # ipath = '/Volumes/新加卷/60秒上王者'
    # opath = '/Users/hardcattle/test/videos/output_videos'
    hvd = int(raw_input("input head of video duration(-1代表无片头): "))
    tvd = int(raw_input("input tail of video duration:(-1代表无片尾）"))
    if hvd > -1 or tvd > -1:
        cutVideo = cutVideo(ipath,opath,hvd,tvd)
        cutVideo.start()
    else:
        print 'not'
    


