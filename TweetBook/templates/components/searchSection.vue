<template>
  <div id="search-section">
    <!-- Searchbar -->
    <div class="searchbar d-flex justify-content-between">
      <div class="d-flex align-items-center">
        <b-button
          class="advanced-search-button ml-4 mr-2"
          id="advanced-filter-activator"
          @click="showAdvancedSearchPopover()"
        >
          <em class="fas fa-sliders-h"></em>
        </b-button>

        <b-form-input
          autocomplete="off"
          id="search-input-id"
          class="search-input mx-2"
          placeholder="Ricerca..."
          spellcheck="false"
          type="text"
          @input="onInput()"
          v-model="page_copy.search_parameters.keywords"
        ></b-form-input>

        <b-button
          id="search-button-id"
          class="search-button mx-2"
          @click="search()"
        >
          <em class="fas fa-search"></em>
        </b-button>
      </div>
      <div class="d-flex align-items-center">
        <b-button
          @click="saveSearch(page)"
          class="search-button mx-2"
          id="download-button"
        >
          Download
          <em class="fas fa-file-download"></em>
        </b-button>

        <b-button
          @click="openFileSelector()"
          class="search-button ml-2 mr-4"
          id="upload-button"
        >
          Upload
          <em class="fas fa-file-upload"></em>
        </b-button>
        <b-form-file
          id="upload-form-file"
          accept=".json"
          multiple
          plain
          v-model="loaded_files"
          @input="onFileInput"
          style="display: none"
        ></b-form-file>
      </div>
    </div>

    <!-- Empty search -->
    <div v-if="!page.name" class="search-empty">
      <em class="far fa-sticky-note fa-3x"></em>
      <h3>Nessuna ricerca effettuata...</h3>
    </div>
    <!-- Search done -->
    <div v-else class="search-done">
      <div class="search-container d-flex flex-column">
        <div
          class="selection-bar d-flex justify-content-between align-items-center px-3"
        >
          <div style="color: rgb(22, 159, 242)">
            <div v-if="page.selected_tweets.length">
              <strong>Selezionati (${page.selected_tweets.length})</strong>
            </div>
          </div>
          <div class="d-flex">
            <div
              @click="page.selected_tweets = page.tweets.slice()"
              style="color: rgb(22, 159, 242); cursor: pointer"
            >
              <strong>Seleziona tutti</strong>
            </div>
            <div class="px-2">•</div>
            <div
              @click="page.selected_tweets = []"
              style="color: rgb(22, 159, 242); cursor: pointer"
            >
              <strong>Deseleziona tutti</strong>
            </div>
          </div>
        </div>
        <div class="search-tweets-container p-2">
          <div
            @click="showTweet(tweet.id_str)"
            class="search-tweets-wrapper"
            v-for="(tweet, index) in page.tweets"
            :key="index"
          >
            <div class="d-flex px-3 py-2 justify-content-between">
              <div class="d-flex">
                <div class="picture-wrapper">
                  <b-avatar
                    class="mr-2"
                    :src="tweet.user.profile_image_url"
                  ></b-avatar>
                </div>
                <div class="content-wrapper d-flex flex-column">
                  <div class="d-flex flex-wrap">
                    <div class="mr-1">
                      <strong>${tweet.user.name}</strong>
                    </div>
                    <div style="color: rgb(101, 119, 134)">
                      @${tweet.user.screen_name}
                    </div>
                  </div>
                  <div class="tweet-text">${tweet.text}</div>
                </div>
              </div>
              <div class="select-wrapper d-flex align-items-center pl-4">
                <div
                  class="px-2 py-1 checkboxes"
                  @click="toggleSelection(tweet, page.selected_tweets)"
                  style="border-radius: 7px; cursor: pointer"
                  :style="{
                    backgroundColor:
                      page.selected_tweets.indexOf(tweet) != -1
                        ? 'rgb(22, 159, 242)'
                        : 'rgb(101, 119, 134)',
                  }"
                >
                  <div style="width: 13px">
                    ${page.selected_tweets.indexOf(tweet) != -1 ? "✔" : "✘"}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="extra-content-wrapper">
        <!-- Images -->
        <div id="images" class="images-wrapper no-scrollbar d-flex flex-wrap">
          <div
            v-for="(media, index) in current_page_media"
            :key="index"
            class="image-container-parent"
          >
            <div
              class="image-container-child d-flex align-items-center justify-content-center"
              :style="{ backgroundImage: 'url(' + media.url + ')' }"
              @click="showTweet(media.tweet_id)"
            ></div>
          </div>
        </div>
        <!-- Tweet Lookup -->
        <div
          id="tweet-lookup-wrapper"
          class="p-2 tweet-lookup-wrapper no-scrollbar"
        >
          <div
            id="tweet-lookup"
            class="tweet-lookup-container d-flex align-items-center flex-column"
          >
            <p style="text-align: center" class="my-auto">
              Seleziona un tweet per vederne i dettagli
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Avenced search popup -->
    <b-popover
      target="advanced-filter-activator"
      triggers="click blur"
      placement="topright"
      class="popover"
      ref="popover"
    >
      <template #title>
        <h3 class="mx-1 mt-1" style="color: white">Ricerca avanzata</h3>
      </template>
      <template #default>
        <div class="d-flex flex-column mb-2 mx-1">
          <b-form-checkbox
            class="popover_item"
            @input="onInput()"
            v-model="page_copy.search_parameters.stream"
            >Ricerca in streaming
          </b-form-checkbox>
          <div style="color: white; font-size: large">Includi</div>
          <b-form-checkbox
            class="popover_item"
            @input="onInput()"
            v-model="page_copy.search_parameters.retweets"
            >Retweet
          </b-form-checkbox>
          <b-form-checkbox
            class="popover_item"
            @input="onInput()"
            v-model="page_copy.search_parameters.replies"
            >Risposte
          </b-form-checkbox>
          <label for="input-utente">Utente</label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-utente"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.user"
          ></b-form-input>
          <label for="input-luogo">Luogo</label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-luogo"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.location"
          ></b-form-input>
          <label for="input-hashtag">Hashtag</label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-hashtag"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.hashtag"
          ></b-form-input>
          <label for="input-tag">Tag</label>
          <b-form-input
            class="search-input"
            size="sm"
            id="input-tag"
            placeholder="Cerca..."
            spellcheck="false"
            type="text"
            @input="onInput()"
            v-model="page_copy.search_parameters.tag"
          ></b-form-input>
        </div>
      </template>
    </b-popover>
  </div>
</template>

<script>
module.exports = {
  delimiters: ["${", "}"],
  data: function () {
    return {
      loaded_files: [],
      page_copy: null,
    };
  },
  props: {
    page: Object,
  },
  computed: {
    /* Media della ricerca attuale */
    current_page_media: function () {
      let array = [];
      this.page.tweets.forEach((tweet) => {
        if (tweet.extended_entities) {
          tweet.extended_entities.media.forEach((media) => {
            array = array.concat({
              url: media.media_url,
              tweet_id: tweet.id_str,
            });
          });
        }
      });
      return array;
    },
  },
  methods: {
    search() {
      /* Salvo la pagina in una variabile per tenerne
      traccia nel caso prima che la ricerca finisca
      viene cambiata pagina */
      let page = this.page;
      let params = this.page.search_parameters;
      let url =
        "search/?keywords=" +
        encodeURIComponent(params.keywords) +
        "&retweets=" +
        encodeURIComponent(params.retweets) +
        "&replies=" +
        encodeURIComponent(params.replies) +
        "&user=" +
        encodeURIComponent(params.user) +
        "&location=" +
        encodeURIComponent(params.location) +
        "&hashtag=" +
        encodeURIComponent(params.hashtag) +
        "&tag=" +
        encodeURIComponent(params.tag);
      fetch(url)
        .then((response) => response.json())
        .then((data) => {
          page.tweets = data.statuses;
          page.name = params.keywords;
          this.$emit("recent-search-done", page);
          /* DEBUG */
          console.log("Data:");
          console.log(data);
        });
    },
    streamTweets(keywords) {
      this.active_page.tweets = [];
      this.active_page.matching_rules = [];
      this.active_page.includes = [];

      params = this.active_page.search_parameters;
      keywords =
        keywords +
        (params.retweets ? " " : " -is:retweet") +
        (params.replies ? " " : " -is:reply") +
        (params.user == "" ? " " : " from:" + params.user) +
        (params.hashtag == "" ? " " : " #" + params.hashtag) +
        (params.tag == "" ? " " : " @" + params.tag);
      console.log("Search keywords: " + keywords);

      // Send keywords into websocket connection
      if (!this.stream_connection_open) {
        this.stream_connection_open = true;
        this.socket = new WebSocket("ws://localhost:5000");
        this.socket.onopen = () => this.socket.send(keywords);
      } else {
        this.socket.send(keywords);
        this.changing_stream_query = true;
      }
      // Update page on tweet received from streaming
      this.socket.addEventListener("message", function (event) {
        /*console.log('nuovo tweet con: ', JSON.parse(event.data).matching_rules[0].id) // TODO per fermare la visualizzazione dello stream appena cambio la query dello streaming, fino a che non arriva qualcosa secondo le nuove regole
                if (vm.changing_stream_query) {
                    console.log('sto cambiando');
                    var x = JSON.parse(JSON.stringify(vm.active_page.matching_rules));
                    console.log('vecchio: ', x, x[0]);
                    if (JSON.parse(event.data).matching_rules[0].id == x[0]){ 
                        console.log('non va bene, new/old: ', JSON.parse(event.data).matching_rules[0].id, vm.active_page.matching_rules[0]);
                        return;
                    }
                    else {
                        vm.changing_stream_query = false;
                        console.log('va bene, new/old: ', JSON.parse(event.data).matching_rules[0].id, vm.active_page.matching_rules[0]);
                    }
                } else {*/
        if (!vm.active_page.search_parameters.stream) return;
        let tweet = JSON.parse(event.data);
        vm.active_page.tweets.unshift(tweet.data);
        vm.active_page.includes.unshift(tweet.includes);
        vm.active_page.matching_rules.unshift(tweet.matching_rules[0].id);

        if (vm.active_page.tweets.length > 100) {
          vm.active_page.tweets.pop();
          vm.active_page.includes.pop();
          vm.active_page.matching_rules.pop();
        }

        //}
      });
    },
    /* Mostra nel pannello il tweet corrispondente a "tweet_id" */
    showTweet(tweet_id) {
      let tweet_wrapper = document.getElementById("tweet-lookup");
      if (tweet_wrapper && tweet_id) {
        /* Clear the tweet lookup panel */
        while (tweet_wrapper.hasChildNodes()) {
          tweet_wrapper.removeChild(tweet_wrapper.lastChild);
        }
        /* Create the spinner for the tweet lookup panel */
        let opts = {
          lines: 12, // The number of lines to draw
          length: 38, // The length of each line
          width: 17, // The line thickness
          radius: 45, // The radius of the inner circle
          scale: 0.4, // Scales overall size of the spinner
          corners: 1, // Corner roundness (0..1)
          speed: 1, // Rounds per second
          rotate: 0, // The rotation offset
          animation: "spinner-line-fade-quick", // The CSS animation name for the lines
          direction: 1, // 1: clockwise, -1: counterclockwise
          color: "#ffffff", // CSS color or array of colors
          fadeColor: "transparent", // CSS color or array of colors
          top: "50%", // Top position relative to parent
          left: "0%", // Left position relative to parent
          shadow: "0 0 1px transparent", // Box-shadow for the lines
          className: "spinner", // The CSS class to assign to the spinner
          position: "relative", // Element positioning
        };
        new Spin.Spinner(opts).spin(tweet_wrapper);
        /* Start the lookup */
        twttr.widgets
          .createTweet(tweet_id, tweet_wrapper, {
            theme: "dark",
            lang: "it",
          })
          .then(() => {
            tweet_wrapper.removeChild(tweet_wrapper.firstChild);
            tweet_wrapper.firstChild.style["display"] = "block";
          });
      }
    },
    toggleSelection(object, array) {
      if (array.indexOf(object) != -1) {
        array.splice(array.indexOf(object), 1);
      } else {
        array.push(object);
      }
    },
    /* Scarica un file JSON di 'page' */
    saveSearch(page) {
      if (page.tweets.length) {
        let data = JSON.stringify(page);
        let blob = new Blob([data], {
          type: "application/json",
        });
        let filename = page.name;
        let link = document.createElement("a");
        link.download = filename;
        //Funzione createObjectURL cross-browser
        let createObjectURL =
          (window.URL || window.webkitURL || {}).createObjectURL ||
          function () {};
        link.href = createObjectURL(blob);
        link.click();
      }
    },
    /* Aggiunge una nuova pagina contenente i dati del file
        al percorso "file" */
    loadSearch(file) {
      if (file) {
        let path = file;
        let fileReader = new FileReader();
        let _this = this;
        fileReader.onload = function (event) {
          try {
            let text = event.target.result;
            let json = JSON.parse(text);
            if (_this.jsonFileErrors(json)) {
              throw "jsonshemeerror";
            }
            _this.$emit("load-search", json);
          } catch (err) {
            if (err == "jsonschemeerror")
              window.alert("file .json non contenente tweet");
            else window.alert("Il file deve essere di tipo JSON!");
          }
        };
        fileReader.readAsText(path, "utf-8");
      } else {
        window.alert("Inserire un file da caricare");
      }
    },
    /* Mostra la finestra di ricerca avanzata */
    showAdvancedSearchPopover() {
      this.$refs.popover.$emit("open");
    },
    openFileSelector() {
      document.getElementById("upload-form-file").click();
    },
    /* Funzione che va a controllare l'integrità dell'oggetto page */
    jsonFileErrors(json) {
      if (!json.hasOwnProperty("name")) return true;
      if (!json.hasOwnProperty("tweets")) return true;
      if (!json.hasOwnProperty("search_parameters")) return true;
      //if (!json.hasOwnProperty('selected_images')) return true;
      return false;
    },
    onInput() {
      this.$emit("params-update", this.page_copy.search_parameters);
    },
    onFileInput() {
      for (let i = 0; i < this.loaded_files.length; i++) {
        this.loadSearch(this.loaded_files[i]);
      }
      this.loaded_files = [];
    },
  },
  watch: {
    /* When prop is updated, the value is stored into the copy */
    page(new_value) {
      this.page_copy = new_value;
    },
  },
  created: function () {
    this.page_copy = this.page;
  },
};
</script>

<style>
#search-section {
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.searchbar {
  height: var(--searchbar-height);
  width: calc(100vw - var(--sidebar-width));
  border-bottom: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.advanced-search-button {
  background-color: transparent;
  border: none;
  outline: none;
  font-size: 20px;
}

.advanced-search-button * {
  color: rgb(22, 159, 242);
}

.search-input {
  background-color: rgb(37, 51, 65);
  border-radius: 22px;
  width: 300px;
  height: 70%;
  border: 1px solid rgba(0, 0, 0, 0);
  box-sizing: border-box;
  color: white;
}

.search-input:focus {
  background-color: rgba(0, 0, 0, 0);
  border-color: rgb(29, 161, 242);
  color: white;
}

.search-button {
  background-color: transparent;
  border: none;
  outline: none;
  font-size: 20px;
}

.search-button * {
  color: #aab8c2;
}

.search-empty {
  display: flex;
  flex-direction: column;
  width: calc(100vw - var(--sidebar-width));
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  justify-content: center;
  align-items: center;
}

.search-done {
  display: flex;
  width: calc(100vw - var(--sidebar-width));
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  color: white;
}

.search-container {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  border-right: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.selection-bar {
  height: var(--searchbar-height);
  width: calc((100vw - var(--sidebar-width)) / 2);
  border-bottom: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.search-tweets-container {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc(
    100vh - var(--pagesbar-height) - var(--searchbar-height) -
      var(--searchbar-height)
  );
  overflow-y: auto;
}

.search-tweets-container::-webkit-scrollbar {
  display: none;
}

.search-tweets-wrapper {
  transition: 0.2s;
  border: 1px solid rgb(47, 51, 54);
  box-sizing: border-box;
  border-radius: 16px;
  width: 100%;
  background-color: rgb(0, 0, 0);
  color: white;
}

.search-tweets-wrapper:hover {
  transition: 0.2s;
  background-color: rgba(18, 21, 23, 0.7);
}

.extra-content-wrapper {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc(100vh - var(--pagesbar-height) - var(--searchbar-height));
  display: flex;
  flex-direction: column;
}

.images-wrapper {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc((100vh - var(--pagesbar-height) - var(--searchbar-height)) / 2);
  overflow-y: auto;
  border-bottom: rgb(56, 68, 77) 1px solid;
  box-sizing: border-box;
}

.image-container-parent {
  width: calc((100vw - var(--sidebar-width)) / 6);
  height: calc((100vw - var(--sidebar-width)) / 6);
  padding: 5px;
}

.image-container-child {
  height: 100%;
  width: 100%;
  transition: 0.2s;
  background-color: rgb(0, 0, 0);
  border: 1px solid rgb(47, 51, 54);
  box-sizing: border-box;
  border-radius: 16px;
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  cursor: pointer;
}

.image-container-child:hover {
  transition: 0.2s;
  background-color: rgba(18, 21, 23, 0.7);
}

.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.tweet-text {
  line-height: 1.3125;
}

.tweet-lookup-wrapper {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc((100vh - var(--pagesbar-height) - var(--searchbar-height)) / 2);
  overflow-y: auto;
}

.tweet-lookup-container {
  width: calc((100vw - var(--sidebar-width)) / 2);
  height: calc((100vh - var(--pagesbar-height) - var(--searchbar-height)) / 2);
}
</style>
