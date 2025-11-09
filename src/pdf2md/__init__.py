from .server import mcp

def main():
    """PDF to Markdown Conversion Service - Provides MCP service for converting PDF files to Markdown"""
    import os
    import argparse
    import logging
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="PDF to Markdown Conversion Service")
    parser.add_argument("--output-dir", default="./downloads", help="Specify output directory path, default is ./downloads")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Set logging level")
    args = parser.parse_args()
    
    # Import after argument parsing to ensure logger is configured
    from .server import set_output_dir, MINERU_API_KEY, logger, HTTP_CLIENT_TIMEOUT, TASK_MAX_RETRIES, TASK_RETRY_INTERVAL
    
    # Set output directory
    set_output_dir(args.output_dir)
    
    # Configure logging level from command line
    log_level = getattr(logging, args.log_level.upper())
    logger.setLevel(log_level)
    
    # Check API key
    if not MINERU_API_KEY:
        logger.warning("⚠️ API key not set, please set the MINERU_API_KEY environment variable")
        return
    
    # Log configuration info
    logger.info("🚀 PDF to Markdown Conversion Service starting...")
    logger.info(f"📊 Configuration: HTTP_CLIENT_TIMEOUT={HTTP_CLIENT_TIMEOUT}s, TASK_MAX_RETRIES={TASK_MAX_RETRIES}, TASK_RETRY_INTERVAL={TASK_RETRY_INTERVAL}s")
    logger.info(f"📁 Output directory: {args.output_dir}")
    
    try:
        # Run MCP server with connection stability improvements
        logger.info("🔗 Starting MCP server with stdio transport...")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("⏹️ Server stopped by user")
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        raise

__all__ = ['main']