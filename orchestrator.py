from agents.query_agent    import query_agent
from agents.research_agent import research_agent
from agents.analysis_agent import analysis_agent
from agents.review_agent   import review_agent
from agents.report_agent   import report_agent
from agents.email_agent    import email_agent
from datetime import datetime

def run_pipeline(user_query: str, recipient_email: str) -> dict:
    """
    Master pipeline function.
    Runs all 6 agents in sequence.
    Returns complete results dict.
    """

    print(f"\n{'='*55}")
    print(f"🚀 GCC BI Platform Pipeline Started")
    print(f"   Query: {user_query}")
    print(f"   Email: {recipient_email}")
    print(f"   Time:  {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*55}\n")


    start_time = datetime.now()

    results = {
        "query":      user_query,
        "email":      recipient_email,
        "started_at": datetime.now().isoformat(),
        "stages":     {}
    }

    try:
        # Stage 1
        print("[ 1/6 ] Query Agent...")
        t1                         = datetime.now()                     
        query_plan                 = query_agent(user_query)
        results["stages"]["query"] = "✅ completed"
        results["query_plan"]      = query_plan
        print(f"        Done in {(datetime.now()-t1).seconds}s")      

        # Stage 2
        print("\n[ 2/6 ] Research Agent...")
        t2                            = datetime.now()                   
        research_output               = research_agent(query_plan)
        results["stages"]["research"] = "✅ completed"
        results["sources_found"]      = len(research_output["results"])
        print(f"        Done in {(datetime.now()-t2).seconds}s")          

        # Stage 3
        print("\n[ 3/6 ] Analysis Agent...")
        t3                             = datetime.now()                    
        analysis_output                = analysis_agent(research_output)
        results["stages"]["analysis"]  = "✅ completed"
        results["items_before_review"] = analysis_output["total"]
        print(f"        Done in {(datetime.now()-t3).seconds}s")          

        # Stage 4
        print("\n[ 4/6 ] Review Agent...")
        t4            = datetime.now()                                    
        review_output = review_agent(analysis_output)

        # Set stage results BEFORE empty check
        results["stages"]["review"]   = "✅ completed"
        results["items_after_review"] = review_output["total"]
        results["items_rejected"]     = review_output["total_rejected"]
        print(f"        Done in {(datetime.now()-t4).seconds}s")           

        # Stop pipeline if no data found
        if review_output["total"] == 0:
            results["status"] = "no_data"
            results["error"]  = "No data found. Try a more specific query or wait if rate limited."
            print("⚠️ No data found — stopping pipeline.")
            return results

        # Stage 5 — only runs if data exists
        print("\n[ 5/6 ] Report Agent...")
        t5                           = datetime.now()                    
        report_output                = report_agent(review_output)
        results["stages"]["report"]  = "✅ completed"
        results["report_file"]       = report_output["filename"]
        results["report_title"]      = query_plan.get("report_title", "")
        print(f"        Done in {(datetime.now()-t5).seconds}s")           

        # Stage 6 — only runs if data exists
        print("\n[ 6/6 ] Email Agent...")
        t6                           = datetime.now()                      
        email_output                 = email_agent(report_output, recipient_email)
        results["stages"]["email"]   = "✅ completed"
        results["email_sent"]        = email_output["success"]
        print(f"        Done in {(datetime.now()-t6).seconds}s")         

        results["completed_at"] = datetime.now().isoformat()
        results["status"]       = "success"

       
        total_time = (datetime.now() - start_time).seconds

        print(f"\n{'='*55}")
        print(f"✅ Pipeline Complete!")
        print(f"   Sources searched:   {results['sources_found']}")
        print(f"   Items extracted:    {results['items_before_review']}")
        print(f"   Items after review: {results['items_after_review']}")
        print(f"   Items rejected:     {results['items_rejected']}")
        print(f"   Report:             {results['report_file']}")
        print(f"   Email sent:         {results['email_sent']}")
        print(f"   Total time:         {total_time}s")                     
        print(f"{'='*55}\n")

    except Exception as e:
        results["status"] = "failed"
        results["error"]  = str(e)
        print(f"\n❌ Pipeline failed: {e}")

    return results


# Test directly
if __name__ == "__main__":
    run_pipeline(
        user_query      = "Find AI startups in Saudi Arabia",
        recipient_email = "ashali422@gmail.com"
    )