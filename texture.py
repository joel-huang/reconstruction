import argparse
import numpy
import cv2
import numpy as np

def ReverseTransfer(IUV, im):

    TextureIm = np.zeros([24,200,200,3])
    U = IUV[:,:,1]
    V = IUV[:,:,2]

    for index in xrange(1,25):
	x,y = np.where(IUV[:,:,0] == index) # masks: x,y coordinates where part I = current index

	# init empty 2d channels with shape of texture part
	R = np.zeros([200,200])
	G = np.zeros([200,200])
	B = np.zeros([200,200])

	# convert u,v values in the part to the texture map space (flip V)
	tu = (U[x,y])*199./255.
	tv = (255-V[x,y])*199./255.


	R[tv.astype(int),tu.astype(int)] += im[x,y,0]
	G[tv.astype(int),tu.astype(int)] += im[x,y,1]
	B[tv.astype(int),tu.astype(int)] += im[x,y,2]

	# set each texture part to its RGB values
	TextureIm[index-1,:,:,:] = np.transpose(np.dstack((R,G,B)), (1,0,2))


    stack1= np.hstack(TextureIm[0:6,:,:,:])
    stack2= np.hstack(TextureIm[6:12,:,:,:])
    stack3= np.hstack(TextureIm[12:18,:,:,:])
    stack4= np.hstack(TextureIm[18:24,:,:,:])
    ans=[stack1,stack2,stack3,stack4]
    return np.vstack([x for x in ans])

def TransferTexture(TextureIm,im,IUV):
    U = IUV[:,:,1]
    V = IUV[:,:,2]
    #
    R_im = np.zeros(U.shape)
    G_im = np.zeros(U.shape)
    B_im = np.zeros(U.shape)
    ###
    for PartInd in xrange(1,25):    ## Set to xrange(1,23) to ignore the face part.
        tex = TextureIm[PartInd-1,:,:,:].squeeze() # get texture for each part.
        #####
        R = tex[:,:,0]
        G = tex[:,:,1]
        B = tex[:,:,2]
        ###############
        x,y = np.where(IUV[:,:,0]==PartInd)
        u_current_points = U[x,y]   #  Pixels that belong to this specific part.
        v_current_points = V[x,y]
#        import ipdb;ipdb.set_trace()
        r_current_points = R[((255-v_current_points)*199./255.).astype(int),(u_current_points*199./255.).astype(int)]*255
        g_current_points = G[((255-v_current_points)*199./255.).astype(int),(u_current_points*199./255.).astype(int)]*255
        b_current_points = B[((255-v_current_points)*199./255.).astype(int),(u_current_points*199./255.).astype(int)]*255


        ##  Get the RGB values from the texture images.
        R_im[IUV[:,:,0]==PartInd] = r_current_points
        G_im[IUV[:,:,0]==PartInd] = g_current_points
        B_im[IUV[:,:,0]==PartInd] = b_current_points

    generated_image = np.concatenate((B_im[:,:,np.newaxis],G_im[:,:,np.newaxis],R_im[:,:,np.newaxis]), axis =2 ).astype(np.uint8)
    BG_MASK = generated_image==0
    generated_image[BG_MASK] = im[BG_MASK]  ## Set the BG as the old image.
    return generated_image

def get_rgba_texture(img, iuv):
    rgb = ReverseTransfer(iuv,img).astype(np.uint8)
    alpha = np.zeros([800,1200])
    alpha[np.where(rgb>0)[0]] = 255
    rgba=cv2.cvtColor(x,cv2.COLOR_RGB2RGBA)
    rgba[:,:,3]=alpha
    return rgba
