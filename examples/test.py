#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller,OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel
import random
from time import sleep

def topology():

    net = Mininet( controller=Controller, link=TCLink, switch=OVSKernelSwitch )

    print "*** Creating nodes"
    h0 = net.addHost('h0', ip='10.0.0.33/8')
    s0 = net.addSwitch('s0')
    ap1 = net.addAccessPoint( 'ap1', ssid= 'ssid', mode= 'g', channel= '1', position='15,30,0', range='20' )
    ap2 = net.addAccessPoint( 'ap2', ssid= 'ssid', mode= 'g', channel= '6', position='65,30,0', range='20' )
    ap3 = net.addAccessPoint( 'ap3', ssid= 'ssid', mode= 'g', channel= '6', position='230,130,0', range='20' )
    sate10 = net.addAccessPoint( 'sate10', ssid='satellite', mode='g', channel='6', position='37,50,0', range='100' )
    lte20 = net.addAccessPoint( 'lte20', ssid='lte', mode='g', channel='6', position='105,5,0', range='100' )

    stas = []
    for n in range(0, 9):
        stas.append(n)
    for n in range(0, 9):
        stas[n] =  net.addStation( 'sta%s' % (n + 1), mac='00:00:00:00:00:0%s' % (n + 1), ip='10.0.0.%s/8' % (n + 1))
    sta11 = net.addStation('sta11', position='69,25,0')

    c1 = net.addController( 'c1', controller=Controller )

    print "*** Configuring wifi nodes"
    net.configureWifiNodes()

    # Comment out the following two lines to disable AP
    print "*** Enabling association control (AP)"
    #net.associationControl( 'ssf' )        

    print "*** Creating links and associations"
    net.addLink( h0, s0 )
    net.addLink( s0, ap3, bw=20, loss=0.1 )
    net.addLink( ap1, ap2 )
    net.addLink( ap2, ap3, bw=20, loss=0.1 )
    net.addLink( s0, sate10, bw=20, loss=0.1)
    net.addLink( s0, lte20, bw=20, loss=0.1 )

    """plot graph"""
    net.plotGraph(max_x=300, max_y=300)

    net.startMobility(time = 0)
    net.mobility(stas[0], 'start', time = 3, position = '190, 190, 0.0')
    net.mobility(stas[0], 'stop', time = 5, position = '63, 39, 0.0')
    net.mobility(stas[1], 'start', time = 1, position = '190, 130, 0.0')
    net.mobility(stas[1], 'stop', time = 5, position = '90, 100, 0.0')
    net.mobility(stas[2], 'start', time = 0, position = '20, 130, 0.0')
    net.mobility(stas[2], 'stop', time = 5, position = '50, 70, 0.0')
    net.mobility(stas[3], 'start', time = 1, position = '170, 90, 0.0')
    net.mobility(stas[3], 'stop', time = 3, position = '120, 70, 0.0')
    net.mobility(stas[4], 'start', time = 1, position = '170, 90, 0.0')
    net.mobility(stas[4], 'stop', time = 3, position = '100, 75, 0.0')
    for sta in stas[5:]:
        x_start = random.randint(0, 300) 
        y_start = random.randint(0, 300)
        x_stop = random.randint(5, 30)
        y_stop = random.randint(3, 50)
        t_start = random.randint(1, 5)
        t_stop = random.randint(8, 10)
        net.mobility(sta, 'start', time = t_start, position = '%s, %s, 0.0' % (x_start, y_start))
        net.mobility(sta, 'stop', time = t_stop, position = '%s, %s, 0.0' % (x_stop, y_stop))

    net.stopMobility(time = 10)

    print "*** Starting network"
    net.build()
    c1.start()
    ap1.start( [c1] )
    ap2.start( [c1] )
    ap3.start( [c1] )
    sate10.start( [c1] )
    lte20.start( [c1] )
    s0.start( [c1] )

    sleep(5)
    cnt = 1
    for sta in stas:
        cmd = 'iwconfig sta%d-wlan0 disconnect' % (cnt)
        sta.cmd(str(cmd))
        sta.cmd('iwconfig sta%d-wlan0 essid %s ap %s' % (cnt, lte20.params['ssid'][0], lte20.params['mac'][0]))
        cnt += 1
    sta11.cmd('iwconfig sta11-wlan0 essid %s ap %s' % (lte20.params['ssid'][0], lte20.params['mac'][0]))

    #h0.cmd('iperf -s -i 1 > result')
    #cnt = 1
    #for sta in stas:
    #    print('iperf -c -i 1 -t 10 > result%d' % cnt)	
    #    sta.cmd('iperf -c -i 1 -t 10 > result%d' % cnt)	
    #sta11.cmd('iperf -c -i 1 -t 10 > result11')	

    print "*** Running CLI"
    CLI( net )

    print "*** Stopping network"
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'debug' )
    topology()
