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

def myheatmap(n, colorbarlabel=None, **kwargs):
    plt.pcolormesh( listwrap(n.columns),listwrap(n.index), n, **kwargs)
    plt.xlabel(n.columns.name)
    plt.ylabel(n.index.name)
    cbar = plt.colorbar(drawedges=False)
    if colorbarlabel:
        cbar.set_label(colorbarlabel)
 