""" 
Press and hold the left button to accumulate power, release the left button to shoot 
Press the up and down keys to zoom in/out on the monitor view
The game is complete after reaching twenty points 
""" 

import viz
import vizact
import vizcam
import vizinfo

NUM_rockerS       = 3 
NUM_pigeonS     = 10 
MIN_POWER       = 1
MAX_POWER       = 50
SET_NUMS        = 5

viz.setMultiSample(4)
viz.fov(60)
viz.go(viz.FULLSCREEN)
viz.message('The game start!')
vizinfo.InfoPanel(align=viz.ALIGN_RIGHT_TOP)



#viz.mouse.setOverride(True)
#viz.mouse.setVisible(False)

f22=viz.addChild('f-22 FRONT.osgb',scale=(0.0005,0.0005,0.0005))
f22.texture(viz.addTexture('f-22.jpg'))
f22.setPosition([0, 0.8, -6.8])
f22.setEuler([0,0,0])
crosshair = viz.addTexQuad(viz.ORTHO, texture=viz.add('crosshair.png'), size=64)

view = viz.MainView
tracker = vizcam.addWalkNavigate()
tracker.setPosition([0,1.8,0])
viz.link(tracker,view)
viz.mouse.setVisible(False)

viz.link( viz.Mouse , crosshair, srcFlag=viz.WINDOW_PIXELS )
#tracker.setPosition([0,1,0],viz.REL_LOCAL)
viz.link(tracker,f22,offset=(0,-0.3,0.5))
pit = viz.addChild('pit.osgb')
pit.collideMesh()
pit.disable(viz.DYNAMICS)

video = viz.addRenderTexture()

cam = viz.addRenderNode()
cam.fov = 30.0
cam.setSize(1280,720)
cam.setInheritView(False)
cam.setPosition([0, 3, -8])
cam.setEuler(240,90,60)
cam.setRenderTexture(video)
cam.setMultiSample(viz.AUTO_COMPUTE)
cam.setRenderLimit(viz.RENDER_LIMIT_FRAME)

screen = pit.getChild('screen')
screen.texture(video)
cam.renderOnlyIfNodeVisible([screen])

def CameraZoom(inc):
    cam.fov = viz.clamp(cam.fov+inc,5.0,70.0)
    cam.setFov(cam.fov,1.77,0.1,1000)
def CameraTurn(inc):
    cam.setEuler(inc,20,0)
    
vizact.whilekeydown(viz.KEY_UP,CameraZoom,vizact.elapsed(-20.0))
vizact.whilekeydown(viz.KEY_DOWN,CameraZoom,vizact.elapsed(20.0))
vizact.whilekeydown(viz.KEY_LEFT,CameraTurn,vizact.elapsed(20.0))
vizact.whilekeydown(viz.KEY_RIGHT,CameraTurn,vizact.elapsed(-20.0))

CameraZoom(0.0)

def UpdateCamera():
    cam.setEuler(0,20,0)
    cam.lookAt(viz.MainView.getPosition())
vizact.ontimer(0,UpdateCamera)


scorePanel = vizinfo.InfoPanel('Score: 0', icon=False)
scorePanel.score = 0

rockers = []
pigeons = []

viz.phys.enable()


import random

def newP():
    post=[random.uniform(0,5),0,random.uniform(0,5)]
    newTarget = viz.addAvatar('pigeon.cfg',pos=post,scale=[3,3,3])
    newTarget.setEuler([-180,0,0])
    
    shadow = viz.addChild('shadow.wrl',scale=(1,1,1),alpha=0.7,cache=viz.CACHE_CLONE)
    shadow.setParent(newTarget)

    newTarget.collideMesh()
    newTarget.disable(viz.DYNAMICS)
    
    newTarget.addAction(vizact.spin(0,1,0,30))
    print(post)
    newTarget.state(2)
    pigeons.append(newTarget)
    
newP()

for x in range(NUM_rockerS):
    rocker = viz.addChild('rocker.3ds',pos=(0,0,-40),scale=(0.1,0.1,0.1),cache=viz.CACHE_CLONE)
    shadow = viz.addChild('shadow.wrl',alpha=0.7,cache=viz.CACHE_CLONE)
    viz.link(rocker,shadow,mask=viz.LINK_POS).setPos([None,0,None])
    rocker.collideSphere()
    rocker.enable(viz.COLLIDE_NOTIFY)
    rockers.append(rocker)

nextrocker = viz.cycle(rockers)

power = viz.addProgressBar('Power',pos=(0.8,0.1,0))
power.disable()
power.set(0)

resultPanel1 = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER,fontSize=25,icon=False,key=None)
resultPanel1.visible(False)

def ChargePower():
    power.set(power.get()+0.05)

vizact.whilemousedown(viz.MOUSEBUTTON_LEFT,ChargePower)

def shootrocker():
    resultPanel1.visible(False)
    rocker = nextrocker.next()
    line = viz.MainWindow.screenToWorld(viz.mouse.getPosition())
    line.begin=f22.getPosition()
    
    vector = viz.Vector(line.dir)
    vector.setLength(vizmat.Interpolate(MIN_POWER,MAX_POWER,power.get()))

    rocker.setPosition(line.begin)
    rocker.reset()
    rocker.setVelocity(vector)
    rocker.enable(viz.PHYSICS)
    viz.playSound('daodan.wav')
    power.set(0)

vizact.onmouseup(viz.MOUSEBUTTON_LEFT,shootrocker)

TRIAL_SUCCESS = 'You hit all the pigeons!'
HIT_GET = 'You get it!'
HIT_MISS ='You missed '
resultPanel1 = vizinfo.InfoPanel('',align=viz.ALIGN_CENTER,fontSize=25,icon=False,key=None)
resultPanel1.visible(False)



resultPanel2 = vizinfo.InfoPanel('',align=viz.ALIGN_RIGHT_CENTER,fontSize=25,icon=False,key=None)
resultPanel2.visible(True)

t=SET_NUMS


def oncollide(e):
    if e.obj2 in pigeons:
        e.obj2.execute(2)
        viz.playSound('yanzi.wav')
        scorePanel.score += 1
        scorePanel.setText('Score: {}'.format(scorePanel.score))
        e.obj2.remove()
        global t
        t-=1
        resultPanel2.setText('The remaining:{} pigeons'.format(t))
        if scorePanel.score==SET_NUMS:
            viz.playSound('red.wav')
            resultPanel1.setText(TRIAL_SUCCESS)
            resultPanel1.visible(True)
            viz.message('You hit all the pigeons!')
            viz.quit()
        else:
            resultPanel1.setText(HIT_GET)
        newP()
        resultPanel1.visible(True)
        #print()
    
        
    #viz.playSound('bounce.wav')
    
viz.callback(viz.COLLIDE_BEGIN_EVENT,oncollide)

viz.MainView.move([0,0,-7])

viz.playSound('quack.wav',viz.SOUND_PRELOAD)
viz.playSound('bounce.wav',viz.SOUND_PRELOAD)
viz.playSound('yanzi.wav',viz.SOUND_PRELOAD)
