import requests
from html.parser import HTMLParser

URL_TEST_F = input("Enter the URL for the ASCII shape test case: ").strip()

class ArtParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_data_cell = False
        self.in_table = False
        self.data = []
        self.current_row = []
        self.has_content = False

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            if not self.in_table:
                self.in_table = True
        
        if self.in_table:
            if tag == 'tr':
                self.current_row = []
                self.has_content = False

            elif tag == 'td':
                self.in_data_cell = True
                self.current_cell_data = ''

    def handle_data(self, data):
        if self.in_data_cell:
            self.current_cell_data += data

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_data_cell:
            cell_content = self.current_cell_data.strip()
            self.current_row.append(cell_content)
            if cell_content:
                self.has_content = True
            self.in_data_cell = False

        elif tag == 'tr' and self.in_table:
            if self.has_content and len(self.current_row) == 3:
                self.data.append(self.current_row)
            self.current_row = []

        elif tag == 'table':
            self.in_table = False


def fetch_ascii_art(url):
    """
    Fetches the HTML, parses the table, and reconstructs the ASCII art.
    Applies the simple Y-axis inversion required to show the upright 'F'.
    """
    print(f"Fetching URL: {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        response.encoding = 'utf-8' 
        html_content = response.text
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching URL: {e}"

    parser = ArtParser()
    parser.feed(html_content)
    raw_table_data = parser.data

    if not raw_table_data:
        return "Error: Could not find structured 3-column data in the document's table."

    points = []
    
    for row in raw_table_data:
        if len(row) != 3:
            continue
        x_str, char, y_str = row
        try:
            original_x = int(x_str)
            original_y = int(y_str)
            char_clean = char.strip()
            if not char_clean: continue
            points.append((original_x, char_clean, original_y))
        except ValueError:
            continue
            
    if not points:
        return "Error: Found table but no valid (X, Character, Y) points could be extracted."
        
    max_x = max(p[0] for p in points)
    max_y = max(p[2] for p in points)

    grid_height = max_y + 1
    grid_width = max_x + 1

    grid = [[' ' for _ in range(grid_width)] for _ in range(grid_height)]

    for original_x, ch, original_y in points:
        
        final_row = max_y - original_y 
        final_col = original_x
        
        if 0 <= final_row < grid_height and 0 <= final_col < grid_width:
            grid[final_row][final_col] = ch

    art = "\n".join("".join(row) for row in grid)
    return art

if __name__ == "__main__":
    print("\n\n--- Running Test Case Printing the ASCII art ---\n\n\n\n")
    art_f = fetch_ascii_art(URL_TEST_F)
    print("\n\n")
    print(art_f)
    print("\n\n\n\n----------------------------------------------------------")