### ipython으로 plt.show()가 작동하도록 하게 하기

- 먼저 ipython을 실행
- 그 다음, ipython shell에 %pylab을 기입
- 그 다음, %run $script-이름을 기입해서 실행

### Example
> $ ipython  
> In[1] : %pylab  
> In[2] : %run reference.py

이렇게 하면 matplotlib 창이 하나 뜨게 되고, 결과를 확인할 수 있다.

### matplotlib.pyplot 그래프 사용법

- 그래프에서 pan/zoom모드로 들어간 뒤 왼쪽마우스로 드래그하면 이동이 되고, 오른쪽마우스로 드래그하면 Zoom in/Zoom out이 된다.