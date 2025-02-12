import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Example of unpacking a tuple if prices are stored incorrectly
# Assuming low_price, current_price, or high_price might be tuples

def create_price_plot(low_price, current_price, high_price):
    # If any price is a tuple, we extract the first element
    if isinstance(low_price, tuple):
        low_price = low_price[0]
    if isinstance(current_price, tuple):
        current_price = current_price[0]
    if isinstance(high_price, tuple):
        high_price = high_price[0]

    # Ensure all prices are floats (or ints)
    low_price = float(low_price)
    current_price = float(current_price)
    high_price = float(high_price)

    # Cap the current price within the range if it exceeds limits
    capped_price = min(max(current_price, low_price), high_price)

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(6, 2))

    # Plot the range (background line)
    ax.plot([low_price, high_price], [0.5, 0.5], color='#e0e0e0', lw=10, zorder=1)  # Grey background line
    ax.scatter(capped_price, 0.5, color='#1565c0', s=200, zorder=2)  # Blue dot for current price

    # Add annotations
    ax.text(low_price, 0.6, f'Low ₹{low_price}', fontsize=12, verticalalignment='center')
    ax.text(high_price, 0.6, f'High ₹{high_price}', fontsize=12, verticalalignment='center', horizontalalignment='right')
    ax.text(capped_price, 0.4, f'₹{current_price} at Unicorn Store', fontsize=12, verticalalignment='center', color='#1565c0', horizontalalignment='center')

    # Remove the axes for a clean look
    ax.set_axis_off()

    # Save the plot to a BytesIO object to send to the HTML page
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)  # Rewind the data
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')  # Convert to base64 string
    plt.close()  # Close the plot to free up memory
    return plot_url