from app import app

if __name__ == "__main__":
    try:
      import googleclouddebugger
      googleclouddebugger.enable(
        breakpoint_enable_canary=True
      )

    except ImportError:
      pass
    app.run(host='0.0.0.0', port=80)
