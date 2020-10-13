Vue.component('info-page', {
  props:["id"],
  data () {
     return {
       graph: null
     }
  },
  mounted() {
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
      fetch(`/coastviewer/1.1.0/transects/${transect_id}/plot/eeg`, {

      })
      .then(response => { 
        const resp_json =  response.json()
        return resp_json
      }).then(resp_json => {
        const series_object = {type: 'line', smooth: true, seriesLayoutBy: 'row'}
        const series = []
        const selected = {}
        

        Object.keys(resp_json.data).forEach(row => {
          if (resp_json.data[row][0]!=='cross_shore') {
            series.push(series_object)
            selected[resp_json.data[row][0].toString()] = false
          }
        })

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
            source: resp_json.data //data
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
