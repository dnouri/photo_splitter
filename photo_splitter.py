#!/usr/bin/env python
'''
photo_spliter.py - Provides a simple method to split a single image containing
multiple images into individual files.

Created by Greg Lavino
03.16.2010


Note the following packages are required:
 python-tk
 python-imaging
 python-imaging-tk
'''

import PIL
import Image
import ImageTk
import Tkinter
import sys
import os

thumbsize = 600, 600

class Application(Tkinter.Frame):              
    def __init__(self, master=None,filename=None):
        
        Tkinter.Frame.__init__(self, master)   
        self.grid()                    
        self.createWidgets()
        self.croprect_start=None
        self.croprect_end=None
        self.crop_count=0
        self.canvas_rects=[]
        self.crop_rects=[]
        self.current_rect=None
        
        if filename:
            self.filename=filename
            self.loadimage()
        
        
        
    def createWidgets(self):
        self.canvas = Tkinter.Canvas(self,height = 1, width = 1,relief=Tkinter.SUNKEN)
        self.canvas.bind("<Button-1>",self.canvas_mouse1_callback)
        self.canvas.bind("<ButtonRelease-1>",self.canvas_mouseup1_callback)
        self.canvas.bind("<B1-Motion>",self.canvas_mouseb1move_callback)
        
        self.quitButton = Tkinter.Button ( self, text='Quit',
            command=self.quit )
        self.resetButton = Tkinter.Button ( self, text='Reset',
            command=self.reset )
        
        self.undoButton = Tkinter.Button ( self, text='Undo',
            command=self.undo_last )
        
        self.goButton = Tkinter.Button ( self, text='Go',
            command=self.start_cropping )
        
        self.canvas.grid(row=0,columnspan=4)
        self.goButton.grid(row=1,column=0)
               
        self.resetButton.grid(row=1,column=1)
        self.undoButton.grid(row=1,column=2) 
        self.quitButton.grid(row=1,column=3)
        
    def canvas_mouse1_callback(self,event):
        self.croprect_start=(event.x,event.y)

    def canvas_mouseb1move_callback(self,event):
        if self.current_rect:
            self.canvas.delete(self.current_rect)
        x1=self.croprect_start[0]
        y1=self.croprect_start[1]
        x2=event.x
        y2=event.y
        bbox = (x1,y1,x2,y2)
        cr = self.canvas.create_rectangle(bbox )
        self.current_rect=cr
    
    def canvas_mouseup1_callback(self,event):
        self.croprect_end=(event.x,event.y)
        self.set_crop_area()
        self.canvas.delete(self.current_rect)
        self.current_rect=None
        

    def set_crop_area(self):
        r=Rect( self.croprect_start ,self.croprect_end )
        
        
        # adjust dimensions
        r.clip_to(self.image_thumb_rect)
        
        # ignore rects smaller than this size
        if min(r.h,r.w) < 10:
            return
        
        self.drawrect(r)
        self.crop_rects.append(r.scale_rect(self.scale) )

    
    
    def undo_last(self):
        if self.canvas_rects:
            r = self.canvas_rects.pop()
            self.canvas.delete(r)
        
        if self.crop_rects:
            self.crop_rects.pop()    
        
    def drawrect(self,rect):
        bbox=(rect.left, rect.top,rect.right, rect.bottom)
        cr = self.canvas.create_rectangle(bbox , activefill="",fill="red",stipple="gray25" )
        self.canvas_rects.append(cr)
    
    def displayimage(self):
        self.photoimage=ImageTk.PhotoImage(self.image_thumb)
        w,h = self.image_thumb.size
        self.canvas.configure(width=w,height=h)

        self.canvas.create_image(0,0,anchor=Tkinter.NW,image=self.photoimage)         
    
    def reset(self):
        self.canvas.delete(Tkinter.ALL)
        self.canvas_rects=[]
        self.crop_rects=[]

        self.displayimage()

    def loadimage(self):
        

        self.image = Image.open(self.filename)
        print self.image.size
        self.image_rect = Rect(self.image.size)
        
        self.image_thumb=self.image.copy()
        self.image_thumb.thumbnail(thumbsize)
        
        self.image_thumb_rect = Rect(self.image_thumb.size)
        
        #imt.thumbnail(thumbsize, Image.ANTIALIAS)
        self.displayimage()
        x_scale  = float(self.image_rect.w) / self.image_thumb_rect.w
        y_scale  = float(self.image_rect.h) / self.image_thumb_rect.h
        self.scale=(x_scale,y_scale)

    def newfilename(self,filenum):
        f,e = os.path.splitext(self.filename)
        return '%s_%s%s'%(f,filenum, e)

    def start_cropping(self):
        cropcount = 0
        for croparea in self.crop_rects:
            cropcount+=1
            f = self.newfilename(cropcount)
            print f,croparea
            self.crop(croparea,f)

    def crop(self,croparea,filename):
        ca=(croparea.left,croparea.top,croparea.right,croparea.bottom)
        newimg = self.image.crop(ca)
        newimg.save(filename)

class Rect(object):
    def __init__(self, *args):
        self.set_points(*args)

    def set_points(self, *args):
        if len(args)==2:
            pt1 = args[0]
            pt2 = args[1]
        elif len(args) == 1:
            pt1 = (0,0)
            pt2 = args[0]
        elif len(args)==0:
            pt1 = (0,0)
            pt2 = (0,0)
        

        x1, y1 = pt1
        x2, y2 = pt2
        
        self.left = min(x1, x2)
        self.top = min(y1, y2)
        self.right = max(x1, x2)
        self.bottom = max(y1, y2)
        
        self._update_dims()


    def clip_to(self,containing_rect):
        cr = containing_rect
        self.top    = max(self.top , cr.top)
        self.bottom = min(self.bottom, cr.bottom)
        self.left   = max(self.left , cr.left)
        self.right  = min(self.right, cr.right)
        self._update_dims()
            
    def _update_dims(self):
        '''added to provide w and h dimensions'''
       
        self.w = self.right - self.left
        self.h = self.bottom - self.top
        
    def scale_rect(self,scale):
        x_scale  = scale[0]
        y_scale  = scale[1]
        
        r=Rect()
        r.top = int(self.top * y_scale)
        r.bottom = int(self.bottom * y_scale)
        r.right = int(self.right * x_scale)
        r.left = int(self.left * x_scale)
        r._update_dims()
        
        return r

    def __repr__(self):
        return '(%d,%d)-(%d,%d)'%(self.left,self.top,self.right,self.bottom)



def main():
    if len(sys.argv)>1:
        filename=sys.argv[1]
    else:
        print "Need a filename"
        return
        
    app = Application(filename=filename)                    
    app.master.title("Photo Splitter") 
    app.mainloop()                  

if __name__=='__main__':main()



