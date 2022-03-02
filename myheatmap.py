## myheatmap() plots a heatmap similar to seaborn heatmap but with numeric axes.

## A note on the need for listwrap():
# Ideally the dimensions of X and Y should be one greater than those of C; 
# if the dimensions are the same, then the last row and column of C will be ignored.

# create a listwrap that wraps around the list 
# This is what I need for pcolormesh.
def listwrap(currentlist):
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
# You may specify a text label for the colorbar.
# Note that the 'rocket' cmap is a default seaborn heatmap.
def myheatmap(df, colorbarlabel=None, **kwargs):
    plt.pcolormesh(listwrap(df.columns),listwrap(df.index), df, **kwargs)
    plt.xlabel(df.columns.name)
    plt.ylabel(df.index.name)
    ax = plt.gca()
	# Choose aesthetics similar to seaborn heatmap. In particular, no frames.
	
    ax.set_frame_on(False)
    cbar = plt.colorbar(drawedges=False)
    cbar.outline.set_visible(False)
    if colorbarlabel:
        cbar.set_label(colorbarlabel)
    return ax