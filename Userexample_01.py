# 




import thvisa as thv		# import time in the header
import thvisa_spd3303c		# Labornetzteil
import thvisa_oszi			# InfiniiVision

if __name__ == '__main__':
	# step 1: configure Netzteil
	# step 2: configure oszi
	# step 3: run TC
	with labornetzteil() as psu:
		# step 1: configure Netzteil
		# step 1.1: disable channels?
        psu.disable(ch=1)
        psu.disable(ch=2)
        
		# step 1.2: configure netzteil output
        print("major range change to make it kachunck")
        psu.set(ch=1, v_set=30, c_max=0.1)
        psu.set(ch=2, v_set=5, c_max=0.1)
		
		# step 2: configure oszi
		with thvoszi() as osziobj:
			# step 2.1: autoscale oszi
			osziobj.autoscale(ch=1)
			# step 2.1: manually scale oszi
			osziobj.scale(ch=1, t=0.001, v=5, trig=4.0)
			
			# step 3: run TC
			# step 3.1: enable channel 1
			psu.enable(ch=1)
			
			# step 3.2: check oszi
			osziobj.screenie()

		# step 3.3: disable channel 1 at the end of your TC
        psu.disable(ch=1)
