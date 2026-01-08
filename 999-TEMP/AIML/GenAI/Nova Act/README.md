```python
from nova_act import NovaAct

# Launch a controlled browser session starting at amazon.com

with NovaAct(starting_page="https://www.amazon.com") as agent:
    # Step 1: Search for a product
    print("Executing: search for a coffee maker")
    agent.act("search for a coffee maker")

    # Step 2: Select the first search result
    print("Executing: select the first result")
    agent.act("select the first result")

    # Step 3: Click the "Add to Cart" button
    print("Executing: click the 'Add to Cart' button")
    agent.act("scroll until you see 'Add to Cart', then click 'Add to Cart'")

# The with-block ensures the browser is closed when done.
print("Script finished.")
```

