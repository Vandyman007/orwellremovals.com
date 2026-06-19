#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the whole site (all HTML + sitemap + llms.txt).
Run: python3 tools/build.py   then   npm run build:css   (or: npm run build)
"""
import importlib, importlib.util, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

RENDERERS = ["render_home", "render_locations", "render_services", "render_core",
             "render_blog"]

def main():
    for name in RENDERERS:
        mod = importlib.import_module(name)
        mod.build()
    for tool in ["build-sitemap.py", "build-llms-txt.py"]:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), tool)
        spec = importlib.util.spec_from_file_location(tool.replace("-", "_").replace(".py", ""), path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.main()
    print("\nBuild complete. Now run: npm run build:css  (regenerates css/site.min.css)")

if __name__ == "__main__":
    main()
