<template>
  <div id="graph-section" class="p-2">
    <div class="half-height">
      <div id="chart_bar" class="full-dimensions"></div>
    </div>
    <div class="half-height d-flex">
      <div id="chart_pie" class="half-width"></div>
      <div id="word_cloud" class="half-width"></div>
    </div>
  </div>
</template>

<script>
module.exports = {
  data: function () {
    return {
      chart_bar: null,
      chart_pie: null,
      word_cloud: null,
      cloud_series: null,
      word_filters: {
        max_number_cloud: 50,
        max_number_pie: 10,
        min_char_length: 4, //le proposizioni hanno tutte tre lettere
        min_frequency: 1,
      },
      refresh_interval: null,
    };
  },
  props: {
    page: Object,
    update_needed: Boolean,
    export: Function,
  },
  computed: {
    get_words: function () {
      let tweets_text = "";
      this.page.tweets.forEach((el) => {
        tweets_text += el.text;
      });
      return tweets_text;
    },
    get_frequencies: function () {
      //producing json with frequencies of words without quality control
      let text = this.get_words.toLowerCase(); //avoid duplicates
      let wf = new WordFreq(text.split(/ |\n|,/));
      wf.set("string");
      let obj = wf.list();
      return obj;
    },
    is_streaming: function () {
      return (
        !(this.page.search_parameters.stream != true) &&
        this.page.tweets.length > 0
      );
    },
  },
  methods: {
    initGraphs() {
      am4core.useTheme(am4themes_dark);
      am4core.useTheme(am4themes_animated);
      this.chart_pie = am4core.create("chart_pie", am4charts.PieChart);
      this.chart_bar = am4core.create("chart_bar", am4charts.XYChart);
      this.word_cloud = am4core.create(
        "word_cloud",
        am4plugins_wordCloud.WordCloud
      );
    },
    updateGraphsData() {
      this.resetGraphs();
      if (this.page.tweets.length != 0) {
        // Chart Bar
        for (let i = 0; i < this.page.tweets.length; i++) {
          var bool = false;
          if (this.page.search_parameters.stream) {
            if (this.page.tweets[i].places != null) {
              if (this.page.tweets[i].places[0].name != null) {
                if (this.chart_bar != null) {
                  for (
                    let j = 0;
                    j < this.objLength(this.chart_bar.data);
                    j++
                  ) {
                    if (
                      this.page.tweets[i].places[0].name ==
                      this.chart_bar.data[j].country
                    ) {
                      this.chart_bar.data[j].visits++;
                      bool = true;
                    }
                  }
                  if (!bool) {
                    this.chart_bar.data.push({
                      country: this.page.tweets[i].places[0].name,
                      visits: 1,
                    });
                  }
                } else {
                  this.chart_bar.data.push({
                    country: this.page.tweets[i].places[0].name,
                    visits: 1,
                  });
                }
              }
            }
          }
          if (this.page.tweets[i].place != null) {
            if (this.chart_bar != null) {
              for (let j = 0; j < this.objLength(this.chart_bar.data); j++) {
                if (
                  this.page.tweets[i].place.name ==
                  this.chart_bar.data[j].country
                ) {
                  this.chart_bar.data[j].visits++;
                  bool = true;
                }
              }
              if (!bool) {
                this.chart_bar.data.push({
                  country: this.page.tweets[i].place.name,
                  visits: 1,
                });
              }
            } else {
              this.chart_bar.data.push({
                country: this.page.tweets[i].place.name,
                visits: 1,
              });
            }
          }
        }
        this.chart_bar.scrollbarX = new am4core.Scrollbar();
        let categoryAxis = this.chart_bar.xAxes.push(
          new am4charts.CategoryAxis()
        );
        categoryAxis.dataFields.category = "country";
        categoryAxis.renderer.grid.template.location = 0;
        categoryAxis.renderer.minGridDistance = 30;
        if (this.objLength(this.chart_bar.data) > 14) {
          categoryAxis.renderer.labels.template.horizontalCenter = "right";
          categoryAxis.renderer.labels.template.verticalCenter = "middle";
          categoryAxis.renderer.labels.template.rotation = 270;
        } else {
          categoryAxis.renderer.labels.template.horizontalCenter = "middle";
          categoryAxis.renderer.labels.template.verticalCenter = "right";
          categoryAxis.renderer.labels.template.rotation = 0;
        }

        categoryAxis.tooltip.disabled = true;
        categoryAxis.renderer.minHeight = 110;
        let valueAxis = this.chart_bar.yAxes.push(new am4charts.ValueAxis());
        valueAxis.renderer.minWidth = 50;
        // Create series
        let series = this.chart_bar.series.push(new am4charts.ColumnSeries());
        series.sequencedInterpolation = true;
        series.dataFields.valueY = "visits";
        series.dataFields.categoryX = "country";
        series.tooltipText = "[{categoryX}: bold]{valueY}[/]";
        series.columns.template.strokeWidth = 0;
        series.tooltip.pointerOrientation = "vertical";
        series.columns.template.column.cornerRadiusTopLeft = 10;
        series.columns.template.column.cornerRadiusTopRight = 10;
        series.columns.template.column.fillOpacity = 0.8;
        // on hover, make corner radiuses bigger
        let hoverState = series.columns.template.column.states.create("hover");
        hoverState.properties.cornerRadiusTopLeft = 0;
        hoverState.properties.cornerRadiusTopRight = 0;
        hoverState.properties.fillOpacity = 1;
        // Cursor
        this.chart_bar.cursor = new am4charts.XYCursor();

        // Word Cloud
        let new_cloud_data = this.getFilteredFrequencies(true);
        if (new_cloud_data.length) {
          this.word_cloud.data = new_cloud_data;
          this.cloud_series = this.word_cloud.series.push(
            new am4plugins_wordCloud.WordCloudSeries()
          );
          this.cloud_series.dataFields.word = "word";
          this.cloud_series.dataFields.value = "count";
          this.cloud_series.randomness = 0.3;
          this.cloud_series.minFontSize = 10;

          //colors
          let twitter_blue = "#169FF2";
          this.cloud_series.labels.template.fill = am4core.color(twitter_blue);

          //tooltips and events
          this.cloud_series.labels.template.tooltipText =
            "{word}:\n[bold]{value}[/]";
          let parent = this;
          this.cloud_series.labels.template.events.on("hit", function (e) {
            parent.$emit("related-search", e);
          });
        }

        // Chart Pie
        let new_pie_data = this.getFilteredFrequencies(false);
        if (new_pie_data.length) {
          this.chart_pie.data = new_pie_data;
          let pieSeries = this.chart_pie.series.push(new am4charts.PieSeries());
          pieSeries.dataFields.value = "count";
          pieSeries.dataFields.category = "word";
          pieSeries.slices.template.stroke = am4core.color("#fff");
          pieSeries.slices.template.strokeOpacity = 1;
          // This creates initial animation
          pieSeries.hiddenState.properties.opacity = 1;
          pieSeries.hiddenState.properties.endAngle = -90;
          pieSeries.hiddenState.properties.startAngle = -90;
          this.chart_pie.hiddenState.properties.radius = am4core.percent(0);
        }
      }
    },
    resetGraphs() {
      // Chart pie
      if (this.chart_pie.series.length) this.chart_pie.series.removeIndex(0);
      this.chart_pie.dispose();
      this.chart_pie = am4core.create("chart_pie", am4charts.PieChart);

      //Chart bar
      if (this.chart_bar.series.length) this.chart_bar.series.removeIndex(0);
      document.getElementById("chart_bar").innerHTML = "";
      this.chart_bar.dispose();
      this.chart_bar = am4core.create("chart_bar", am4charts.XYChart);

      //Chart cloud
      if (this.word_cloud.series.length) this.word_cloud.series.removeIndex(0);
      document.getElementById("word_cloud").innerHTML = "";
      this.word_cloud.dispose();
      this.word_cloud = am4core.create(
        "word_cloud",
        am4plugins_wordCloud.WordCloud
      );
    },
    objLength(obj) {
      var l = 0;
      for (var x in obj) {
        if (obj.hasOwnProperty(x)) {
          l++;
        }
      }
      return l;
    },
    getFilteredFrequencies: function (cloudData) {
      let obj = this.get_frequencies;
      let filtered = [];
      let counter = 0;
      //ordering the object per frequencies
      obj.sort(function (firstEl, secondEl) {
        return secondEl.count - firstEl.count;
      });
      let max_number = cloudData
        ? this.word_filters.max_number_cloud
        : this.word_filters.max_number_pie;
      obj.forEach((el) => {
        if (
          el.word.length >= this.word_filters.min_char_length &&
          el.count >= this.word_filters.min_frequency &&
          counter < max_number
        ) {
          //utilizzo solamente le parole che presentano caratteri alfabetici
          if (/^[a-zA-Z]+$/.test(el.word)) {
            filtered.push(el);
            counter++;
          }
        }
      });
      return filtered;
    },
  },
  watch: {
    update_needed(new_value) {
      if (new_value) {
        this.updateGraphsData();
        this.$emit("graph-updated");
      }
    },
    is_streaming(new_value) {
      if (new_value) {
        if (!this.refresh_interval)
          this.refresh_interval = setInterval(() => {
            this.updateGraphsData();
          }, 30000);
      } else {
        clearInterval(this.refresh_interval);
        this.refresh_interval = null;
      }
    },
    export(new_value) {
      if (new_value) {
        this.chart_pie.exporting
          .getImage("png")
          .then((chart_pie) => this.chart_bar.exporting.getImage("png"))
          .then((chart_bar) => this.word_cloud.exporting.getImage("png"))
          .then((word_cloud) => {
            new_value(chart_pie, chart_bar, word_cloud);
          });
      }
    },
  },
  mounted: function () {
    this.initGraphs();
  },
};
</script>

<style>
#graph-section {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.full-dimensions {
  width: 100%;
  height: 100%;
}

.half-height {
  width: 100%;
  height: 50%;
}

.half-width {
  width: 50%;
  height: 100%;
}
</style>
