import arcade
import arcade.gui

from shadow_of_doubt import constants


class OptionsMenu(arcade.gui.UIMouseFilterMixin, arcade.gui.UIAnchorLayout):
    def __init__(
        self,
        parent_manager: arcade.gui.UIManager,
        title: str,
        dropdown_options: list[str],
        backgound_child: arcade.gui.UIWidget,
    ):
        super().__init__(size_hint=(1, 1))
        self.parent_manager = parent_manager
        self.background_child = backgound_child

        # Setup frame which will act like the window.
        frame = self.add(arcade.gui.UIAnchorLayout(width=800, height=700, size_hint=None))
        frame.with_padding(all=20)
        button_texture = arcade.load_texture(constants.ASSETS_DIR / "button_texture.png")
        texture = arcade.gui.NinePatchTexture(0, 0, 0, 0, button_texture)
        frame.with_background(texture=texture)

        back_button = arcade.gui.UIFlatButton(text="Back", width=250)
        # The type of event listener we used earlier for the button will not work here.
        back_button.on_click = self.on_click_back_button

        title_label = arcade.gui.UILabel(text=title, align="center", font_size=20, multiline=False)
        # Adding some extra space around the title.
        title_label_space = arcade.gui.UISpace(height=30)

        # Align toggle and label horizontally next to each other
        toggle_group = arcade.gui.UIBoxLayout(vertical=False, space_between=5)
        # Create dropdown with a specified default.
        dropdown = arcade.gui.UIDropdown(
            default=dropdown_options[0], options=dropdown_options, height=20, width=250
        )

        widget_layout = arcade.gui.UIBoxLayout(align="left", space_between=10)
        widget_layout.add(title_label_space)
        widget_layout.add(title_label_space)
        widget_layout.add(title_label)
        widget_layout.add(title_label_space)
        widget_layout.add(toggle_group)
        widget_layout.add(dropdown)

        widget_layout.add(back_button)

        frame.add(child=widget_layout, anchor_x="center_x", anchor_y="top")

    def on_click_back_button(self, event):
        # Removes the widget from the manager.
        # After this the manager will respond to its events like it previously did.
        self.parent_manager.remove(self)
        self.parent_manager.remove(self.background_child)
