return {
  {
    "olimorris/onedarkpro.nvim",
    priority = 1000,
    opts = {
      colors = {
        onedark = {
          bg = "#242424",
          comment = "#6c7380",
        },
      },
      styles = {
        comments = "italic",
        keywords = "italic",
        functions = "bold",
        types = "bold",
        strings = "NONE",
        variables = "NONE",
      },
      options = {
        cursorline = true,
        transparency = false,
        terminal_colors = true,
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "onedark",
    },
  },
}
