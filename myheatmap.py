"""
My heatmap functions similarly to seaborn.heatmap but it makes a plot with
numeric axes.
"""
import matplotlib.pyplot as plt 
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar



# Create a listwrap that wraps around the list 
# This is what I need for pcolormesh.
def listwrap(currentlist):
    # Ideally the dimensions of X and Y should be one greater than those of C; 
    # if the dimensions are the same, then the last row and column of C will be ignored.
    listwrap = [0] * (len(currentlist)+1)
    for i in range(len(currentlist)):
        try:
            listwrap[i+1] = ((currentlist[i]+currentlist[i+1])/2)
        except IndexError:
            pass
    topstep = listwrap[2]-listwrap[1]
    listwrap[0]=listwrap[1]-topstep
    botstep = listwrap[-2]-listwrap[-3]
    listwrap[-1]=listwrap[-2]+botstep
    return listwrap

# df is a pandas dataframe
# myheatmap is supposed to work almost exactly like seaborn heatmap. 
# the 'rocket' cmap is the same as the default seaborn heatmap.
# kwargs go to pcolormesh().
def myheatmap(df, colorbarlabel=None, cmap = 'magma', 
              draw_scalebar = False,
              scalebarargs={'size':10, 
                            'label':'10 μm', 
                            'loc':'upper right', 
                            'pad':.3, 
                            'color':'k', 
                            'frameon':False, 
                            'size_vertical':0.6},
              return_cbar = False,
              draw_cbar = True,
              cbarargs={'drawedges':False},
              **kwargs):
    plt.pcolormesh( listwrap(df.columns),listwrap(df.index), df, cmap=cmap, **kwargs)
    plt.xlabel(df.columns.name)
    plt.ylabel(df.index.name)
    ax = plt.gca()
	# Choose aesthetics similar to seaborn heatmap. In particular, no frames.
	
    ax.set_frame_on(False)
    
    if draw_scalebar:
        ax.axis('equal');
        
        plt.xlabel('')
        plt.ylabel('')
        topx = df.columns.max()
        boty = df.index.min()
        plt.yticks([]) # remove y ticks
        plt.xticks([])
    
        scalebar = AnchoredSizeBar(ax.transData,
                            bbox_to_anchor=(topx,boty), bbox_transform=ax.transData,
                            **scalebarargs)

        ax.add_artist(scalebar)
    
    if draw_cbar:
        cbar = plt.colorbar(**cbarargs)
        cbar.outline.set_visible(False)
        if colorbarlabel:
            cbar.set_label(colorbarlabel)
        if return_cbar:
            return ax, cbar
        else:
            return ax
    else:
        return ax # cannot return colorbar if it's not drawn
