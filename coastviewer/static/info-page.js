Vue.component('info-page', {
  props:["id"],
  data () {
     return { 
       graph: null
     }
  },
  mounted() {
    console.log('id',this.id)
    this.createGraph()
    this.updateGraph()
  },
  methods: {
    exportGraph(){ 
      let src = this.graph.getDataURL({
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      let download = document.createElement('a')
      download.href = src
      download.download = 'screenshot.png'
      download.click();
    },
    createGraph(){
      var dom = document.getElementById("echart-container")
      this.graph = echarts.init(dom)
      
    },
    updateGraph(){
      const transect_id = this.id
      fetch(`http://localhost:5000/coastviewer/1.1.0/transects/${transect_id}/plot/eeg`, {
    
      })
      .then(response => {
        const result = response.json()
        return result
      })
      .then(json => {
        const data = JSON.parse(json.data)
        
        const series_object = {type: 'line', smooth: true, seriesLayoutBy: 'row'}
        const series = []
        const selected = {}
        
        console.log (typeof data)
        console.log ('length', data.length)
        data.forEach(row => {
          if (row[0]!=='cross_shore') {
            series.push(series_object)
            selected[row[0].toString()] = false 
          }
        })
        console.log('series', series)
        console.log('selected', selected["1965"])
     /*    for (var i = 0; i< (data.length-1); i++) {
          
          series.push(series_object)
        }
 */
        let options = {

          legend: {
            padding: [0, 0, 0, 0],
            itemGap: 2,
            selector: [
              {
                type: 'all',
                // can be any title you like
                title: 'All'
            }
          ],
            selectorPosition: 'start',
            selectorItemGap: 0.1,
            selectorButtonGap: 2,
            selected: selected
          },
          tooltip: {
            trigger: 'axis'
          },
          dataset: {
             source: data
          },
          xAxis: {type: 'category',
                  name: 'Cross shore',
                  interval: 5,
                  nameTextStyle:{ 
                    fontWeight: "bold",
                    fontSize: 13  
                } 
          },
          yAxis: {gridIndex: 0,
                  name: 'z',
                  nameLocation: "start",
                  nameTextStyle:{ 
                    fontWeight: "bold",
                    fontSize: 16
                } 
          },
          series: series
        } 
        this.graph.clear()
        console.log('options', options)
        this.graph.setOption(options)  
      })

    }
  },
  template: '#info-page'

})
new Vue({
  el: '#app',
  data: {
    fixed: true,
    title: 'Transect info page'
  }
})
