package main

func main() {
	runCrawler()
}

//func queueCrawler() {
//	// Instantiate default collector
//	c := colly.NewCollector(
//		colly.AllowURLRevisit(),
//		colly.MaxDepth(1),
//	)
//
//	// create a request queue with 2 consumer threads
//	q, _ := queue.New(
//		2,                                           // Number of consumer threads
//		&queue.InMemoryQueueStorage{MaxSize: 10000}, // Use default queue storage
//	)
//
//	c.OnRequest(func(r *colly.Request) {
//		fmt.Println("visiting", r.URL)
//		//if r.ID < 15 {
//		//	r2, err := r.New("GET", fmt.Sprintf("%s?x=%v", url, r.ID), nil)
//		//	if err == nil {
//		//		q.AddRequest(r2)
//		//	}
//		//}
//	})
//
//	// Identify interesting links
//	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
//		link := e.Attr("href")
//		// Print link
//		fmt.Println(link)
//		// Visit link found on page on a new thread
//		//e.Request.Visit(link)
//		q.AddURL(link)
//	})
//
//	//c.OnResponse(func(r *colly.Response) {
//	//	body := string(r.Body)
//	//	fmt.Print("test")
//	//	fmt.Println("body length of %s %d", r.Request.URL, len(body))
//	//})
//
//	for _, url := range getUrls() {
//		q.AddURL(url)
//	}
//	// Consume URLs
//	q.Run(c)
//}
