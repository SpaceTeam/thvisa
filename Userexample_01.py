#import thvisa as thv		# only needed in children spd3303c and infiniivision itself
import spd3303c_thvisa as PSU		# Lab PSU
import InfiniiVision_thvisa as osci			# InfiniiVision Oszi

if __name__ == '__main__':
	# step 1: configure PSU
	# step 2: configure oszi
	# step 3: run TC
	with PSU.spd3303c() as psu:
		# step 1: open PSU session as "with-context"
		# step 1.1: setup PSU
		psu.disable(ch=1)
		psu.disable(ch=2)

		# step 1.2: configure netzteil output

		psu.set(ch=1, v_set=30, c_max=0.1)
		psu.set(ch=2, v_set=5, c_max=0.1)

		# step 2: configure oszi
		with osci.InfiniiVision() as osziobj:
			# step 2.1: autoscale oszi
			osziobj.autoscale(ch=1)
			# step 2.1: manually scale oszi
			osziobj.scale(ch=1, t=0.001, v=5, trig=4.0)

			# step 3: run a TC
			#mytestcase.something()

			# step 3.1: enable channel 1
			psu.enable(ch=1)

			# step 3.2: check oszi
			osziobj.screenie()

		# note: frome hereon osziobj is closed
		
		# step 4.0: disable channel 1 at the end of your TC
		psu.disable(ch=1)

	# note: frome hereon psu is closed
	
	# step 4.1: make output pdf with pweave, or something, at least with a screenshot of the osci
	# .. pdf ..
		
		

