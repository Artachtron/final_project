from project.src.platform.display import Display


class TestDisplay:
    def test_create_display(self):
        display = Display(display_id=0,
                        block_size=30,
                        dimensions=(40,32)) 
       
        assert type(display) == Display
        
    def test_display_fields(self):
        display = Display(display_id=0,
                          block_size=30,
                          dimensions=(40,32)) 
        
        display.init()
        
        assert {'dimensions', 'block_size',
                'window_width', 'window_height', 'clock',
                'tick_counter','screen'}.issubset(vars(display))
        
        assert display.dimensions == (40,32)
        assert display.id == 0
        assert display.block_size == 30
        assert display.window_width == display.block_size * display.dimensions[0]
        assert display.window_height == display.block_size * display.dimensions[1]
        assert display.tick_counter == 0
